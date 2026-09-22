"""Isolated active-document confirmation regressions. Never drive Office or capture."""

import importlib.util
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

INSTALLED = Path('/Users/lizhiguo/.autocycle/native_office.py')
MAINTAINED = Path('/Users/lizhiguo/Documents/Developer/autocycle/native_office.py')
PATCH = Path(__file__).with_name('active-document-confirmation.patch')

DEFECTIVE_CHECK = 'if {active} is not targetDoc then error "Unexpected active document"'

OLD_CONFIRM = '''    def confirm_view(self, app, path, request):
        active = 'active workbook' if app == 'excel' else 'active document'
        check = f'if {active} is not targetDoc then error "Unexpected active document"\\n'
        args = (path,)
        if app == 'excel':
            check += 'if (name of active sheet of targetDoc) is not (item 2 of argv) then error "Unexpected worksheet"\\n'
            args += (request['worksheet'],)
        else:
            check += f'if selection start of selection of window 1 of targetDoc is not {request.get("start", 0)} then error "Unexpected Word selection"\\n'
        check += 'set rect to bounds of window 1 of targetDoc\\nreturn (item 1 of rect as text) & "," & (item 2 of rect as text) & "," & (item 3 of rect as text) & "," & (item 4 of rect as text)'
        result = self.script(app, self.find(app, path, check)+'\\nerror "Fixed slot is not open"', *args)
        return [int(float(n)) for n in result.split(',')]
'''

NEW_CONFIRM = '''    @staticmethod
    def confirm_owned_identity(path, expected, observed):
        # Full POSIX paths only. Filename equality is not identity: the same
        # basename at another location, a blank reading, or a specifier-only
        # match must not reach capture.
        slot = str(Path(path))
        expected = (expected or '').strip()
        observed = (observed or '').strip()
        if not expected or not observed:
            raise NativeError('Active document identity unavailable expected:'+expected+' observed:'+observed,'native_capture')
        if expected != slot:
            raise NativeError('Owned document path mismatch expected:'+slot+' observed:'+expected,'native_capture')
        if observed != expected:
            raise NativeError('Unexpected active document expected:'+expected+' observed:'+observed,'native_capture')

    def confirm_view(self, app, path, request):
        active = 'active workbook' if app == 'excel' else 'active document'
        # Compare POSIX paths, not AppleScript object specifiers. Excel's
        # `active workbook is not targetDoc` raises -2700 even when both
        # refer to the owned slot because the specifiers are distinct.
        check = (
            'try\\n'
            'set expectedId to POSIX path of ((full name of targetDoc) as text)\\n'
            'set observedId to POSIX path of ((full name of '+active+') as text)\\n'
            'on error errMsg number errNum\\n'
            'error "Active document identity unavailable (" & errNum & "): " & errMsg\\n'
            'end try\\n'
        )
        args = (path,)
        if app == 'excel':
            check += 'if (name of active sheet of targetDoc) is not (item 2 of argv) then error "Unexpected worksheet"\\n'
            args += (request['worksheet'],)
        else:
            check += f'if selection start of selection of window 1 of targetDoc is not {request.get("start", 0)} then error "Unexpected Word selection"\\n'
        check += 'set rect to bounds of window 1 of targetDoc\\nreturn expectedId & tab & observedId & tab & (item 1 of rect as text) & "," & (item 2 of rect as text) & "," & (item 3 of rect as text) & "," & (item 4 of rect as text)'
        result = self.script(app, self.find(app, path, check)+'\\nerror "Fixed slot is not open"', *args)
        parts = result.split('\\t')
        if len(parts) != 3:
            raise NativeError('Active document identity unavailable: malformed identity reply','native_capture')
        self.confirm_owned_identity(path, parts[0], parts[1])
        return [int(float(n)) for n in parts[2].split(',')]
'''


def apply_repair(source):
    if OLD_CONFIRM not in source:
        raise AssertionError('Installed confirm_view does not match the diagnosed defect')
    return source.replace(OLD_CONFIRM, NEW_CONFIRM, 1)


def load_repaired():
    text = apply_repair(INSTALLED.read_text())
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name) / 'native_office.py'
    path.write_text(text)
    spec = importlib.util.spec_from_file_location('repaired_native_office', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._keep_tmp = tmp
    return module


def png(path):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    rows = b''.join(b'\0' + bytes([(x + y) % 256 for x in range(320 * 3)]) for y in range(240))
    path.write_bytes(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', 320, 240, 8, 2, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(rows))
        + chunk(b'IEND', b'')
    )


class DiagnosisTests(unittest.TestCase):
    def test_installed_and_maintained_still_use_specifier_equality(self):
        installed = INSTALLED.read_text()
        maintained = MAINTAINED.read_text()
        self.assertEqual(installed, maintained)
        self.assertIn(DEFECTIVE_CHECK, installed)
        confirm = installed.split('def confirm_view', 1)[1].split('def capture', 1)[0]
        self.assertNotIn('POSIX path of ((full name of', confirm)
        self.assertIn(DEFECTIVE_CHECK, PATCH.read_text())

    def test_repair_removes_specifier_equality_and_keeps_shared_word_checks(self):
        repaired = apply_repair(INSTALLED.read_text())
        confirm = repaired.split('def confirm_view', 1)[1].split('def capture', 1)[0]
        self.assertNotIn(DEFECTIVE_CHECK, confirm)
        self.assertIn('POSIX path of ((full name of targetDoc)', confirm)
        self.assertIn("POSIX path of ((full name of '+active+') as text)", confirm)
        self.assertIn("active = 'active workbook' if app == 'excel' else 'active document'", confirm)
        self.assertIn('Unexpected worksheet', confirm)
        self.assertIn('Unexpected Word selection', confirm)
        self.assertIn('name of active sheet of targetDoc', confirm)
        self.assertIn('selection start of selection of window 1 of targetDoc', confirm)
        self.assertIn('Fixed slot is not open', confirm)
        self.assertNotIn('if active workbook is not targetDoc', confirm)
        self.assertIn('def confirm_owned_identity', repaired)
        # Ownership / lock / open-return path is unchanged.
        self.assertIn('Office open did not return the fixed slot reference and a fresh lock', repaired)
        self.assertIn('Fixed slot ownership changed; refusing to control another document', repaired)


class IdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.office = load_repaired()

    def test_owned_matching_paths_pass(self):
        slot = '/tmp/autocycle-office/excel-view.xlsx'
        self.office.MacOffice.confirm_owned_identity(slot, slot, slot)

    def test_different_document_rejected(self):
        slot = '/tmp/autocycle-office/excel-view.xlsx'
        other = '/Users/lizhiguo/Documents/other.xlsx'
        with self.assertRaises(self.office.NativeError) as raised:
            self.office.MacOffice.confirm_owned_identity(slot, slot, other)
        self.assertIn('expected:'+slot, str(raised.exception))
        self.assertIn('observed:'+other, str(raised.exception))

    def test_same_name_different_path_rejected(self):
        slot = '/tmp/autocycle-office/excel-view.xlsx'
        decoy = '/tmp/other/excel-view.xlsx'
        with self.assertRaises(self.office.NativeError) as raised:
            self.office.MacOffice.confirm_owned_identity(slot, slot, decoy)
        self.assertIn(decoy, str(raised.exception))
        with self.assertRaises(self.office.NativeError) as raised:
            self.office.MacOffice.confirm_owned_identity(slot, decoy, decoy)
        self.assertIn('Owned document path mismatch', str(raised.exception))

    def test_filename_only_is_not_identity(self):
        slot = '/tmp/autocycle-office/excel-view.xlsx'
        with self.assertRaises(self.office.NativeError):
            self.office.MacOffice.confirm_owned_identity(slot, slot, 'excel-view.xlsx')
        with self.assertRaises(self.office.NativeError):
            self.office.MacOffice.confirm_owned_identity(slot, 'excel-view.xlsx', 'excel-view.xlsx')

    def test_ambiguous_or_blank_identity_rejected(self):
        slot = '/tmp/autocycle-office/excel-view.xlsx'
        for expected, observed in (('', slot), (slot, ''), (None, slot), (slot, None), ('   ', slot)):
            with self.subTest(expected=expected, observed=observed):
                with self.assertRaises(self.office.NativeError) as raised:
                    self.office.MacOffice.confirm_owned_identity(slot, expected, observed)
                self.assertIn('identity unavailable', str(raised.exception))


class ConfirmViewTests(unittest.TestCase):
    def setUp(self):
        self.office = load_repaired()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.slot = Path(self.tmp.name) / 'excel-view.xlsx'
        self.slot.write_bytes(b'slot')
        self.word = Path(self.tmp.name) / 'word-view.docx'
        self.word.write_bytes(b'slot')
        self.backend = self.office.MacOffice()
        self.bodies = []
        self.backend.is_open = lambda app, path: (app, str(path)) in self.backend.opened

    def _own(self, app, path):
        self.backend.opened[(app, str(path))] = (self.backend.reference(app, path), ('lock',))

    def _script(self, expected, observed, rect='40,40,800,600', error=None):
        def script(app, body, *args, **kwargs):
            self.bodies.append(body)
            if error:
                raise self.office.NativeError(error, 'native_capture')
            return expected + '\t' + observed + '\t' + rect
        self.backend.script = script

    def test_owned_excel_document_returns_bounds(self):
        self._own('excel', self.slot)
        self._script(str(self.slot), str(self.slot))
        bounds = self.backend.confirm_view('excel', self.slot, {'worksheet': 'Overview'})
        self.assertEqual(bounds, [40, 40, 800, 600])
        body = self.bodies[-1]
        self.assertIn('full name of active workbook', body)
        self.assertNotIn('is not targetDoc', body)
        self.assertIn('Unexpected worksheet', body)
        self.assertIn('set targetDoc to workbook "excel-view.xlsx"', body)

    def test_owned_word_document_uses_same_path_identity(self):
        self._own('word', self.word)
        self._script(str(self.word), str(self.word), '10,20,300,400')
        bounds = self.backend.confirm_view('word', self.word, {'start': 0})
        self.assertEqual(bounds, [10, 20, 300, 400])
        body = self.bodies[-1]
        self.assertIn('full name of active document', body)
        self.assertIn('Unexpected Word selection', body)
        self.assertNotIn('active workbook', body)
        self.assertNotIn('is not targetDoc', body)

    def test_different_document_does_not_return_bounds(self):
        self._own('excel', self.slot)
        other = str(Path(self.tmp.name) / 'other.xlsx')
        self._script(str(self.slot), other)
        with self.assertRaises(self.office.NativeError) as raised:
            self.backend.confirm_view('excel', self.slot, {'worksheet': 'Overview'})
        self.assertIn(other, str(raised.exception))

    def test_same_name_different_path_does_not_return_bounds(self):
        self._own('excel', self.slot)
        decoy = str(Path(self.tmp.name) / 'decoy' / 'excel-view.xlsx')
        self._script(str(self.slot), decoy)
        with self.assertRaises(self.office.NativeError):
            self.backend.confirm_view('excel', self.slot, {'worksheet': 'Overview'})

    def test_identity_query_error_is_not_swallowed(self):
        self._own('excel', self.slot)
        self._script(str(self.slot), str(self.slot), error='Active document identity unavailable (-50): parameter error')
        with self.assertRaises(self.office.NativeError) as raised:
            self.backend.confirm_view('excel', self.slot, {'worksheet': 'Overview'})
        self.assertIn('identity unavailable', str(raised.exception))

    def test_malformed_identity_reply_is_not_accepted(self):
        self._own('excel', self.slot)
        self.backend.script = lambda *a, **k: '40,40,800,600'
        with self.assertRaises(self.office.NativeError) as raised:
            self.backend.confirm_view('excel', self.slot, {'worksheet': 'Overview'})
        self.assertIn('malformed identity reply', str(raised.exception))

    def test_lost_ownership_never_queries_identity(self):
        self._script(str(self.slot), str(self.slot))
        with self.assertRaises(self.office.NativeError) as raised:
            self.backend.confirm_view('excel', self.slot, {'worksheet': 'Overview'})
        self.assertIn('Fixed slot is not open', str(raised.exception))
        self.assertFalse(any('expectedId' in body or 'full name of active' in body for body in self.bodies))


class CaptureBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.office = load_repaired()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source.xlsx'
        self.source.write_bytes(b'authoritative')

    def _workspace(self, expected=None, observed=None, drop_ownership=False, identity_error=None):
        backend = self.office.MacOffice()
        backend.events = []
        slot_holder = {}

        def open_slot(app, path):
            backend.opened[(app, str(path))] = (backend.reference(app, path), ('lock',))
            slot_holder['path'] = path
            backend.events.append(('open', app, path))

        def close_slot(app, path, save):
            backend.opened.pop((app, str(path)), None)
            backend.events.append(('close', app, path, save))

        def is_open(app, path):
            if drop_ownership and any(event[0] == 'position' for event in backend.events):
                backend.opened.pop((app, str(path)), None)
                return False
            return (app, str(path)) in backend.opened

        def script(app, body, *args, **kwargs):
            backend.events.append(('script', body))
            if identity_error:
                raise self.office.NativeError(identity_error, 'native_capture')
            path = slot_holder['path']
            exp = str(path) if expected is None else expected
            obs = str(path) if observed is None else observed
            return exp + '\t' + obs + '\t40,40,800,600'

        def capture(path, bounds):
            backend.events.append(('capture', path, bounds))
            png(path)

        backend.open = open_slot
        backend.close = close_slot
        backend.is_open = is_open
        backend.script = script
        backend.position = lambda app, path, request: backend.events.append(('position', app, path)) or [40, 40, 800, 600]
        backend.capture = capture
        backend.frontmost = lambda: ''
        backend.restore = lambda bundle: backend.events.append(('restore', bundle))
        ws = self.office.Workspace(self.root / '.git' / 'autocycle', backend, wait_seconds=.01, poll_seconds=.001)
        return ws, backend

    def _request(self):
        return {
            'app': 'excel',
            'source': str(self.source),
            'source_sha256': self.office.digest(self.source),
            'worksheet': 'Overview',
        }

    def test_owned_identity_reaches_capture(self):
        ws, backend = self._workspace()
        result = ws.view(self._request())
        self.assertEqual(result['status'], 'CAPTURED', result)
        self.assertTrue(any(e[0] == 'capture' for e in backend.events))

    def test_different_document_never_reaches_capture(self):
        ws, backend = self._workspace(observed='/tmp/other.xlsx')
        result = ws.view(self._request())
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertFalse(any(e[0] == 'capture' for e in backend.events))
        self.assertIn('Unexpected active document', result['action'])
        self.assertNotIn('screenshot', result)

    def test_same_name_different_path_never_reaches_capture(self):
        ws, backend = self._workspace(observed='/tmp/other/excel-view.xlsx')
        result = ws.view(self._request())
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertFalse(any(e[0] == 'capture' for e in backend.events))

    def test_ambiguous_identity_never_reaches_capture(self):
        ws, backend = self._workspace(expected='', observed='/tmp/autocycle-office/excel-view.xlsx')
        result = ws.view(self._request())
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertFalse(any(e[0] == 'capture' for e in backend.events))
        self.assertIn('identity unavailable', result['action'])

    def test_lost_ownership_never_reaches_capture(self):
        ws, backend = self._workspace(drop_ownership=True)
        result = ws.view(self._request())
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertFalse(any(e[0] == 'capture' for e in backend.events))
        self.assertIn('Fixed slot is not open', result['action'])

    def test_identity_error_never_reaches_capture(self):
        ws, backend = self._workspace(identity_error='Active document identity unavailable (-50): parameter error')
        result = ws.view(self._request())
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertFalse(any(e[0] == 'capture' for e in backend.events))

    def test_word_owned_identity_still_reaches_capture(self):
        source = self.root / 'source.docx'
        source.write_bytes(b'authoritative')
        ws, backend = self._workspace()
        result = ws.view({
            'app': 'word',
            'source': str(source),
            'source_sha256': self.office.digest(source),
            'start': 0,
        })
        self.assertEqual(result['status'], 'CAPTURED', result)
        self.assertTrue(any(e[0] == 'capture' for e in backend.events))


if __name__ == '__main__':
    unittest.main()
