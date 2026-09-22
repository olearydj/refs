"""Portable article projection and explicit, recoverable export."""

import re
import sqlite3
import unicodedata
from contextlib import nullcontext
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from refs import files, languages, projects, sources
from refs.catalog import changed, connect
from refs.models import SourceCreate, doi_arxiv, normalize_arxiv, normalize_doi
from refs.results import RefError

PROFILE = "portable-bibtex-v1"
PROFILE_FINGERPRINT = files.digest(PROFILE.encode())
TEX_ESCAPES = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "$": r"\$", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def tex(value: str) -> str:
    if any(ord(char) < 32 and char not in "\n\t" for char in value):
        raise RefError("invalid_export_value", "Control characters cannot be exported")
    return "".join(TEX_ESCAPES.get(char, char) for char in value)


def title(value: str, protection: dict) -> str:
    value = unicodedata.normalize("NFC", value)
    if protection.get("preserve_case"):
        return "{" + tex(value) + "}"
    terms = sorted({unicodedata.normalize("NFC", term) for term in protection.get("protected_terms", [])}, key=lambda term: (-len(term), term))
    if not terms:
        return tex(value)
    pattern = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(term) for term in terms) + r")(?!\w)")
    parts, end = [], 0
    for match in pattern.finditer(value):
        parts.extend([tex(value[end:match.start()]), "{" + tex(match.group()) + "}"])
        end = match.end()
    return "".join(parts) + tex(value[end:])


def warning(key: str, code: str, message: str, **details) -> dict:
    return dict(code=code, message=message, path=None, details={"citation_key": key, **details}, retryable=False)


BLOCKING_CODES = {'cited_authors_changed', 'issued_date_lost_or_changed', 'work_identity_changed', 'in_text_citation_changed', 'protected_spelling_changed'}
MONTHS = 'jan feb mar apr may jun jul aug sep oct nov dec'.split()


def enforce_losses(losses: list[dict], *, allow_unknown: bool = False) -> None:
    blocked = [loss for loss in losses if loss['code'] in BLOCKING_CODES or loss['class'] in ('blocking', 'structural') or loss['class'] == 'unknown' and not allow_unknown]
    if blocked:
        raise RefError('export_blocked', 'Export has unapplied losses; correct records or explicitly allow unknown mappings', details={'entries': losses})


def serialize(records: list[dict], *, allow_unknown: bool = False) -> tuple[bytes, list[dict]]:
    from refs.models import REGISTRY
    entries, warnings, losses = [], [], []
    seen = set()
    for record in sorted(records, key=lambda row: row['citation_key']):
        key = record['citation_key']

        def assess(code: str, category: str, message: str, path: str = '') -> None:
            loss = dict(code=code, citation_key=key, **{'class': category}, path=path, message=message)
            losses.append(loss)
            if category in ('faithful_incomplete', 'documented_fallback', 'info') or category == 'unknown' and allow_unknown:
                warnings.append(warning(key, code, message, **{'class': category}, mapping_id=path, override=category == 'unknown'))

        if key.casefold() in seen:
            assess('case_colliding_key', 'structural', 'Portable keys differ only by case')
        seen.add(key.casefold())
        create = {name: record[name] for name in SourceCreate.model_fields if name in record}
        try:
            value = SourceCreate.model_validate(create).canonical()
        except ValidationError as exc:
            assess('unsupported_record', 'structural', str(exc))
            continue
        metadata = value['metadata']
        kind = metadata['type']
        types = {row['canonical']: row['portable'] for row in REGISTRY['type_mappings']}
        entry_type = types[kind]
        for field in list(metadata):
            applicable = REGISTRY['field_applicability'].get(field)
            if applicable is not None and kind not in applicable:
                assess('field_omitted', 'documented_fallback', f'{field} has no portable slot for {kind}; retained in catalog', 'metadata.' + field)
                del metadata[field]
        if kind == 'thesis':
            native = value.get('native_type', {}).get('value', '')
            degree = str(metadata.get('genre', '')).casefold().replace('.', '')
            entry_type = 'phdthesis' if native == 'phdthesis' or degree in ('phd', 'phd thesis', 'doctoral thesis', 'dissertation') else 'mastersthesis' if native == 'mastersthesis' or degree in ('masters', "master's thesis", 'master thesis', 'msc', 'ma') else 'misc'
        if kind == 'chapter' and not metadata.get('title'):
            entry_type = 'inbook'
        if entry_type == 'misc' or kind in ('article', 'article-magazine', 'article-newspaper'):
            message = f'{kind} is projected as @{entry_type}'
            if kind in ('webpage', 'post-weblog'):
                message += '; Pandoc may change title quotation marks and emphasis for this portable type'
            assess('type_fallback', 'documented_fallback', message, 'metadata.type')
        for notice in record.get('_projection_notices', []):
            assess(notice['code'], 'info' if notice['code'] == 'title_protection_added' else 'documented_fallback', notice['message'], notice['path'])
        for limitation in record.get('limitations', []):
            if limitation['field']=='language' or limitation['reason'].startswith('Preserved from import:'):
                continue
            if limitation['field'] == 'year' and metadata.get('issued', {}).get('literal'):
                continue
            assess('unassessed_import', 'documented_fallback', f"{limitation['field']}: {limitation['reason']}", limitation['field'])
        fields, notes, used = {}, [], {'type'}
        protection = value.get('title_protection', {})

        def put(target: str, text, *, literal: bool = False) -> None:
            if target == 'doi':
                text = normalize_doi(str(text))
            elif target == 'eprint' and (str(metadata.get('archive','')).casefold()=='arxiv' or value.get('extensions',{}).get('identifiers',{}).get('arxiv')):
                text = normalize_arxiv(str(text))
            rendered = str(text) if literal else tex(str(text))
            if target in fields and fields[target] != rendered:
                assess('work_identity_changed', 'blocking', f'Two facts compete for {target}', target)
            else:
                fields[target] = rendered

        def copy(source: str, target: str) -> None:
            used.add(source)
            if source not in metadata:
                return
            if 'title' in source:
                put(target, title(str(metadata[source]), protection.get(source, {})), literal=True)
            else:
                put(target, metadata[source])

        def render_names(role, names):
            output_names = []
            if any(name.get('dropping-particle') or name.get('non-dropping-particle') for name in names):
                assess('name_particle_fallback', 'documented_fallback', 'Portable names retain the particle before the family name; consumers determine dropping behavior', 'metadata.' + role)
            for name in names:
                if 'literal' in name:
                    output_names.append('{' + tex(name['literal']) + '}')
                    continue
                if any(name.get(flag) for flag in ('static-ordering', 'comma-suffix', 'parse-names')):
                    assess('name_projection_unassessed', 'unknown', 'Consumer handling of this name flag is unassessed', 'metadata.' + role)
                family = ' '.join(name[part] for part in ('dropping-particle', 'non-dropping-particle', 'family') if name.get(part))
                if not family:
                    assess('given_only_name', 'unknown', 'Given-only personal names have unassessed citation behavior', 'metadata.' + role)
                    family = name.get('given', '')
                    output_names.append('{' + tex(family) + '}')
                    continue
                grouped_family = not name.get('dropping-particle') and not name.get('non-dropping-particle') and (len(family.split()) > 1 or family[:1].islower())
                if grouped_family or ' and ' in family or ',' in family:
                    family = '{' + tex(family) + '}'
                else:
                    family = tex(family)
                suffix = tex(name.get('suffix', ''))
                given = tex(name.get('given', ''))
                output_names.append(family + (', ' + suffix + ', ' + given if suffix else ', ' + given if given else ''))
            return ' and '.join(output_names)

        try:
            for role in ('author', 'editor'):
                used.add(role)
                names = list(metadata.get(role, []))
                if role == 'editor' and entry_type in ('book', 'collection'):
                    for name in metadata.get('collection-editor', []):
                        if name not in names:
                            names.append(name)
                if names:
                    put(role, render_names(role, names), literal=True)
            used.update(('collection-editor', 'container-author', 'contributor'))
            if metadata.get('contributor'):
                assess('contributor_omission', 'documented_fallback', 'Contributors remain in the catalog; portable output omits this non-cited role', 'metadata.contributor')
            if metadata.get('collection-editor'):
                assess('collection_editor_fallback', 'documented_fallback', 'Collection editors are emitted as editors on books; their distinct role remains in the catalog', 'metadata.collection-editor')
            if metadata.get('container-author'):
                if entry_type in ('incollection', 'inbook'):
                    put('bookauthor', render_names('container-author', metadata['container-author']), literal=True)
                assess('container_author_omission', 'documented_fallback', 'Container authors are retained in bookauthor on book parts; classic styles may omit this field', 'metadata.container-author')
            if not metadata.get('author') and not fields.get('editor'):
                assess('missing_author', 'faithful_incomplete', 'No author or editor was supplied')
            copy('title', 'title')
            copy('title-short', 'shorttitle')
            if kind in ('article-journal', 'article-magazine', 'article-newspaper'):
                copy('container-title', 'journal')
                if not metadata.get('container-title'):
                    assess('missing_journal', 'faithful_incomplete', 'No journal was supplied')
            elif kind in ('chapter', 'paper-conference'):
                copy('container-title', 'title' if entry_type == 'inbook' else 'booktitle')
            elif 'container-title' in metadata:
                notes.append('Website: ' + str(metadata['container-title']))
                used.add('container-title')
                assess('container_in_note', 'documented_fallback', 'Website name is retained in note', 'metadata.container-title')
            used.add('issued')
            issued = metadata.get('issued')
            if not issued:
                assess('missing_issued', 'faithful_incomplete', 'No issued date was supplied')
            elif issued.get('literal') and not issued.get('date-parts') and not any(issued.get(name) for name in ('circa', 'season')):
                put('year', issued['literal'])
                assess('literal_issued_year', 'documented_fallback', 'Literal issued date written unchanged in year; verify the rendered date', 'metadata.issued')
            elif not issued.get('date-parts') or len(issued['date-parts']) != 1 or any(issued.get(name) for name in ('literal', 'circa', 'season')):
                assess('issued_date_lost_or_changed', 'blocking', 'Portable year/month cannot preserve this issued precision', 'metadata.issued')
            else:
                parts = issued['date-parts'][0]
                put('year', parts[0])
                if len(parts) > 1:
                    put('month', MONTHS[parts[1]-1], literal=True)
                if len(parts) > 2:
                    iso = '-'.join([str(parts[0]), *[f'{number:02d}' for number in parts[1:]]])
                    put('date', iso)
                    notes.append('Issued: ' + iso)
                    assess('issued_day_in_note', 'documented_fallback', 'Supplementary date and note retain the day for portable consumers', 'metadata.issued')
            used.add('language')
            language = metadata.get('language', '')
            langid = languages.portable(language)
            if langid:
                put('langid', langid)
                if not language.casefold().startswith('en') and all(char.isascii() for char in metadata.get('title','')):
                    assess('title_language_review', 'faithful_incomplete', f'Non-English language tag {language} accompanies an ASCII title; verify the language', 'metadata.language')
            else:
                if language:
                    assess('language_unrecognized', 'documented_fallback', 'Unrecognized language retained literally in catalog; no langid emitted', 'metadata.language')
                if any(char.isalpha() and not char.isascii() for char in metadata.get('title', '')):
                    assess('language_unspecified', 'faithful_incomplete', 'Title language is unknown; supply it when known', 'metadata.language')
            for source, target in [('volume', 'volume'), ('issue', 'number'), ('publisher-place', 'address'), ('edition', 'edition'), ('collection-title', 'series'), ('collection-number', 'number'), ('container-title-short', 'shortjournal'), ('chapter-number', 'chapter')]:
                copy(source, target)
            used.add('page')
            if 'page' in metadata:
                put('pages', re.sub(r'(?<=\d)[-–](?=\d)', '--', str(metadata['page'])))
            used.add('publisher')
            if 'publisher' in metadata:
                publisher = tex(str(metadata['publisher']))
                if ' and ' in str(metadata['publisher']):
                    assess('literal_publisher', 'documented_fallback', 'Publisher is one institution; BibLaTeX consumers will not split it on and', 'metadata.publisher')
                    publisher = '{' + publisher + '}'
                if entry_type in ('phdthesis', 'mastersthesis'):
                    put('school', publisher, literal=True)
                elif entry_type == 'techreport':
                    put('institution', publisher, literal=True)
                elif entry_type == 'misc':
                    notes.append(str(metadata['publisher']))
                else:
                    put('publisher', publisher, literal=True)
            used.update(('number', 'archive', 'genre'))
            if kind in ('article', 'manuscript'):
                copy('archive', 'archiveprefix')
                copy('number', 'eprint')
                if (metadata.get('archive') or metadata.get('number')) and not (str(metadata.get('archive','')).casefold()=='arxiv' and value.get('extensions',{}).get('identifiers',{}).get('arxiv')):
                    notes.append(' '.join(str(metadata.get(field, '')) for field in ('archive', 'number')).strip())
                if metadata.get('genre'):
                    notes.append(str(metadata['genre']))
            elif kind in ('patent', 'standard'):
                copy('number', 'number')
                copy('genre', 'type')
                notes.extend(str(metadata[field]) for field in ('genre', 'number') if metadata.get(field))
            else:
                copy('number', 'number')
                if entry_type in ('techreport', 'phdthesis', 'mastersthesis'):
                    copy('genre', 'type')
                elif metadata.get('genre'):
                    notes.append(str(metadata['genre']))
            for field, label in [('authority', ''), ('jurisdiction', ''), ('version', 'Version')]:
                used.add(field)
                if metadata.get(field):
                    notes.append((label + ' ' + str(metadata[field])).strip())
            for field, label in [('event-title', 'Event'), ('event-place', 'Event location'), ('section', 'Section'), ('part-title', 'Part'), ('medium', 'Medium'), ('archive-place', 'Archive location'), ('status', 'Status')]:
                used.add(field)
                if field in metadata:
                    notes.append(label + ': ' + str(metadata[field]))
                    assess('field_in_note', 'documented_fallback', f'{field} is retained in note', 'metadata.' + field)
            for source, target in [('DOI', 'doi'), ('URL', 'url'), ('ISBN', 'isbn'), ('ISSN', 'issn'), ('PMID', 'pmid'), ('PMCID', 'pmcid')]:
                used.add(source)
                if source not in metadata:
                    continue
                text = str(metadata[source])
                if re.search(r'[{}\\\x00-\x1f\x7f]', text):
                    assess('invalid_identifier', 'structural', 'Identifier contains unsafe characters', 'metadata.' + source)
                else:
                    put(target, text, literal=True)
            used.add('accessed')
            if 'accessed' in metadata:
                date = metadata['accessed']
                if date.get('date-parts') and len(date['date-parts']) == 1 and not any(date.get(field) for field in ('literal', 'circa', 'season')):
                    parts = date['date-parts'][0]
                    put('urldate', '-'.join([str(parts[0]), *[f'{number:02d}' for number in parts[1:]]]))
                else:
                    assess('accessed_unassessed', 'unknown', 'Access-date projection is unassessed', 'metadata.accessed')
            for field in ('abstract', 'number-of-pages', 'number-of-volumes'):
                used.add(field)
                if field != 'abstract' and field in metadata:
                    assess('noncitation_omission', 'faithful_incomplete', f'{field} is retained in the catalog', 'metadata.' + field)
            used.add('note')
            if metadata.get('note'):
                notes.insert(0, str(metadata['note']))
            for field in sorted(set(metadata) - used):
                if metadata[field]:
                    assess('unassessed_mapping', 'unknown', f'No assessed portable projection for {field}', 'metadata.' + field)
            for field, extension in value.get('extensions', {}).items():
                if field == 'identifiers':
                    if extension.get('arxiv'):
                        arxiv = extension['arxiv']
                        put('eprint', arxiv)
                        if (derived := doi_arxiv(str(metadata.get('DOI','')))):
                            put('eprint',derived)
                        put('eprinttype', 'arxiv')
                        if entry_type in ('misc', 'unpublished') and arxiv not in record.get('_howpublished', ''):
                            notes.append('arXiv:' + arxiv)
                        assess('arxiv_fallback', 'documented_fallback', 'arXiv identifier retained in eprint fields and a classic-consumer note where needed', 'extensions.identifiers.arxiv')
                    if extension.get('oclc'):
                        assess('oclc_omission', 'documented_fallback', 'OCLC identifier retained in catalog', 'extensions.identifiers.oclc')
                elif field == 'journal_series':
                    put('series', extension)
                    assess('journal_series_fallback', 'documented_fallback', 'Journal series is retained in series; consumer support varies', 'extensions.journal_series')
                elif field == 'patent':
                    for member in extension:
                        if member == 'assignees':
                            names = extension[member]
                            labels = [name.get('literal') or ' '.join(name[part] for part in ('given','dropping-particle','non-dropping-particle','family','suffix') if name.get(part)) for name in names]
                            notes.append('Assignee: ' + '; '.join(labels))
                            assess('assignee_in_note', 'documented_fallback', 'Patent assignees are retained in note, separately from inventors', 'extensions.patent.assignees')
                            continue
                        assess('unassessed_extension', 'unknown', f'No registered projection for patent.{member}', 'extensions.patent.' + member)
                else:
                    assess('unassessed_extension', 'unknown', f'No registered projection for {field}', 'extensions.' + field)
            if record.get('_howpublished'):
                put('howpublished', record['_howpublished'], literal=True)
            if notes:
                put('note', title('; '.join(notes), {'protected_terms': [str(metadata['number'])] if kind in ('patent', 'standard') and metadata.get('number') else []}), literal=True)
            entry = '@' + entry_type + '{' + key + ',\n'
            for name, text in fields.items():
                entry += f'  {name} = {text},\n' if name == 'month' else f'  {name} = {{{text}}},\n'
            entries.append(entry + '}\n')
        except RefError as exc:
            assess('invalid_export_value', 'structural', str(exc))
    enforce_losses(losses, allow_unknown=allow_unknown)
    return '\n'.join(entries).encode('utf-8'), warnings



def preserved_bib_fields(connection, record: dict) -> dict:
    """Only unmodeled howpublished comes from original bytes, never modeled facts."""
    import bibtexparser

    from refs.adapters.bibtex import decode
    values, notices = set(), []
    for row in connection.execute("SELECT raw_bytes FROM originals WHERE source_id=? AND format='bib'", (record['id'],)):
        library = bibtexparser.parse_string(row[0].decode('utf-8'))
        for entry in library.entries:
            if entry.entry_type.lower() != record.get('native_type', {}).get('value'):
                continue
            values.update(field.value for field in entry.fields if field.key.lower() == 'howpublished')
            for field in entry.fields:
                name, raw = field.key.lower(), field.value
                if name in ('author', 'editor', 'publisher', 'institution', 'school') and re.search(r'\\relax|\\[uvH]\s*\{?\s*\\i', raw):
                    notice = dict(code='tex_decoded', path=name, message=f'TeX relax or a dotless-i accent in {name} was decoded to Unicode; Pandoc may render the original spelling differently')
                    if notice not in notices:
                        notices.append(notice)
                canonical = {'journal':'container-title', 'journaltitle':'container-title', 'booktitle':'container-title'}.get(name)
                if canonical:
                    try:
                        before = decode(raw)
                    except ValueError:
                        continue
                    if before != record['metadata'].get(canonical) and before.casefold() == record['metadata'].get(canonical, '').casefold():
                        notices.append(dict(code='container_title_case', path='metadata.'+canonical, message='Container title follows the catalog Title Case convention; verify proper-name capitalization'))
                if name == 'title':
                    terms = record.get('title_protection', {}).get('title', {}).get('protected_terms', [])
                    if 'R' in terms and '{R}' not in raw:
                        notices.append(dict(code='title_protection_added', path='metadata.title', message='The programming-language name R is protected from citation-style lowercasing'))
    if len(values) > 1:
        raise RefError('export_blocked', 'Original howpublished values disagree; inspect the preserved entries', details={'entries':[dict(citation_key=record['citation_key'], code='work_identity_changed', message='Conflicting original howpublished values', **{'class':'blocking'})]})
    return {'_projection_notices': list({(notice['code'], notice['path']): notice for notice in notices}.values())} | ({'_howpublished': next(iter(values))} if values else {})

def target_state(connection, target: Path, project_id: str, *, overwrite: bool = False, adopt: bool = False, candidate_digest: str | None = None) -> tuple[str | None, bool, bool]:
    row = connection.execute("SELECT * FROM export_targets WHERE destination=?", (str(target),)).fetchone()
    current = files.current_digest(target)
    binding_matches = row is not None and row['project_id'] == project_id and row['profile_fingerprint'] == PROFILE_FINGERPRINT
    if adopt and current is not None and not binding_matches:
        proof = connection.execute('SELECT 1 FROM imports WHERE file_digest=? AND finished_at IS NOT NULL', (current,)).fetchone()
        if not proof:
            raise RefError('adoption_requires_import', 'Import these exact bytes before adopting this destination', path=str(target))
        if current != candidate_digest and not overwrite:
            raise RefError('adoption_requires_overwrite', 'Pass --adopt --overwrite to replace the imported bibliography', path=str(target))
        return current, False, False
    if row is None:
        if current is not None:
            raise RefError("unadopted_target", "Existing bibliography has not been adopted", path=str(target))
        return None, False, False
    if row["project_id"] != project_id or row["profile_fingerprint"] != PROFILE_FINGERPRINT:
        raise RefError("target_binding_conflict", "Destination belongs to another project or profile", path=str(target))
    if candidate_digest == files.digest(b'') and current not in (None, candidate_digest) and not overwrite:
        raise RefError('outside_edit', 'Selection is empty; pass --overwrite to replace the non-empty bibliography', path=str(target))
    if current is not None and current == row["baseline_digest"]:
        return current, False, True
    if current is not None and current == row["pending_digest"]:
        return current, True, True
    if current is None and row["baseline_digest"] is None:
        return None, False, True
    if overwrite and current is not None:
        return current, False, True
    raise RefError("outside_edit", "Destination differs from recorded export bytes", path=str(target))


def finish_export(catalog: Path, target: Path, digest: str) -> None:
    with connect(catalog, write=True) as connection:
        count = connection.execute(
            "UPDATE export_targets SET baseline_digest=?, pending_digest=NULL WHERE destination=? AND pending_digest=?",
            (digest, str(target), digest)).rowcount
        if count != 1:
            raise RefError("export_intent_conflict", "Recorded export intent changed", 5)
        changed(connection)


def export(catalog: Path, project_ref: str, output: Path, *, profile: str = PROFILE, dry_run: bool = False, allow_unknown: bool = False, overwrite: bool = False, adopt: bool = False) -> dict:
    if profile != PROFILE:
        raise RefError("unsupported_profile", "This milestone supports portable-bibtex-v1", 2)
    target = files.destination(output)
    with connect(catalog) as connection:
        project = projects.resolve(connection, project_ref)
        selected = [sources.record(connection, row[0]) for row in connection.execute(
            "SELECT s.id FROM sources s JOIN project_sources ps ON s.id=ps.source_id WHERE ps.project_id=? AND ps.cited=1 AND s.state='active' ORDER BY s.citation_key",
            (project["id"],))]
        for record in selected:
            record.update(preserved_bib_fields(connection, record))
        revision = connection.execute("SELECT revision FROM catalog_meta").fetchone()[0]
    data, warnings = serialize(selected, allow_unknown=allow_unknown)
    info = [notice for notice in warnings if notice['details'].get('class') == 'info']
    warnings = [notice for notice in warnings if notice['details'].get('class') != 'info']
    if not selected:
        warnings.append(warning('(selection)', 'empty_selection', f'Wrote {target} (0 entries)'))
    candidate_digest = files.digest(data)
    result = dict(output=str(target), profile=profile, count=len(selected),
                  keys=[record["citation_key"] for record in selected], sha256=candidate_digest,
                  catalog_revision=revision, warnings=warnings, info=info)
    # Preview never acquires the file lock, stages bytes or reconciles intent.
    with nullcontext() if dry_run else files.file_lock(catalog):
        with connect(catalog) as connection:
            current, recoverable, known = target_state(connection, target, project["id"], overwrite=overwrite, adopt=adopt, candidate_digest=candidate_digest)
            if adopt and current is not None and not known:
                from refs import importing
                from refs.adapters import bibtex
                original = target.read_bytes()
                if files.digest(original) != current:
                    raise RefError('outside_edit', 'File changed during adoption; import it again')
                result['import_conflicts'] = [entry for block in bibtex.partition(original) if block['kind'] == 'entry' and (entry := importing.apply_entry(connection, block, str(target), current, dry_run=True))['outcome'] in ('conflict', 'invalid')]
        if dry_run:
            return result | dict(dry_run=True, recoverable=recoverable)
        if recoverable:
            assert current is not None
            finish_export(catalog, target, current)
        if current == candidate_digest:
            if not known:
                with connect(catalog, write=True) as connection:
                    checked, _, _ = target_state(connection, target, project['id'], overwrite=overwrite, adopt=adopt, candidate_digest=candidate_digest)
                    if checked != current:
                        raise RefError('outside_edit', 'File changed during adoption; import it again')
                    connection.execute('INSERT INTO export_targets VALUES (?,?,?,?,NULL) ON CONFLICT(destination) DO UPDATE SET project_id=excluded.project_id, profile_fingerprint=excluded.profile_fingerprint, baseline_digest=excluded.baseline_digest, pending_digest=NULL', (str(target), project['id'], PROFILE_FINGERPRINT, current))
                    changed(connection)
            return result | dict(unchanged=True, recovered=recoverable)
        with files.staged(target, data) as temporary:
            with connect(catalog, write=True) as connection:
                checked, _, _ = target_state(connection, target, project["id"], overwrite=overwrite, adopt=adopt, candidate_digest=candidate_digest)
                if checked != current:
                    raise RefError("outside_edit", "Destination changed while preparing export")
                if known and overwrite:
                    previous = connection.execute("SELECT baseline_digest, pending_digest FROM export_targets WHERE destination=?", (str(target),)).fetchone()
                    if current not in (previous['baseline_digest'], previous['pending_digest']):
                        outside = target.read_bytes()
                        if files.digest(outside) != current:
                            raise RefError('outside_edit', 'Outside bytes changed during preservation')
                        connection.execute("INSERT OR IGNORE INTO originals (id, raw_bytes, sha256, byte_length, format, origin, file_digest, locator) VALUES (?, ?, ?, ?, 'bib', 'export-overwrite', ?, ?)",
                                           (str(uuid4()), outside, current, len(outside), current, str(target)))
                if not known:
                    connection.execute("INSERT INTO export_targets VALUES (?, ?, ?, NULL, ?) ON CONFLICT(destination) DO UPDATE SET project_id=excluded.project_id, profile_fingerprint=excluded.profile_fingerprint, baseline_digest=NULL, pending_digest=excluded.pending_digest", (str(target), project["id"], PROFILE_FINGERPRINT, candidate_digest))
                else:
                    connection.execute("UPDATE export_targets SET pending_digest=? WHERE destination=?", (candidate_digest, str(target)))
                changed(connection)
            files.publish(temporary, target, current)
            try:
                if files.current_digest(target) != candidate_digest:
                    raise RefError("integrity_error", "Published output changed", 5)
                finish_export(catalog, target, candidate_digest)
            except (OSError, sqlite3.Error, RefError) as exc:
                raise RefError("export_published_unrecorded", "Output was published; retry export to reconcile recorded intent", 4,
                               path=str(target), details={"published": True, "cause": str(exc)}) from exc
        return result | dict(unchanged=False, recovered=recoverable)
