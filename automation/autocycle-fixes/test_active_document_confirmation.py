"""Isolated confirmation and identity-reply serialization regressions.

Never drive Office, occupy slots, capture, or invoke process.
"""

import hashlib
import importlib.util
import struct
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path

INSTALLED = Path('/Users/lizhiguo/.autocycle/native_office.py')
MAINTAINED = Path('/Users/lizhiguo/Documents/Developer/autocycle/native_office.py')
SPECIFIER_PATCH = Path(__file__).with_name('active-document-confirmation.patch')
SERIALIZATION_PATCH = Path(__file__).with_name('identity-reply-serialization.patch')
DEPLOYED_RUNTIME_SHA256 = '3317584bd4fa727d489fb0d77f7f3f2599e2d3c18e07321b7791038665dfa3a6'
LEGACY_TAB_RUNTIME_SHA256 = '0db3faee10b0afa3775575ec4197b75cab281f95d4d7c570230b708a9cdb1c5d'

DEFECTIVE_SPECIFIER = 'if {active} is not targetDoc then error "Unexpected active document"'
DEFECTIVE_TAB_RETURN = 'return expectedId & tab & observedId & tab &'
QUOTED_SENTINEL_RETURN = 'return expectedId & "\'+sep+\'" & observedId & "\'+sep+\'" &'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def apply_repair(source):
    if DEFECTIVE_SPECIFIER in source:
        raise AssertionError('Installed runtime unexpectedly still uses specifier equality')
    if DEFECTIVE_TAB_RETURN not in source:
        raise AssertionError('Installed confirm_view does not match the diagnosed tab delimiter')
    patched = source
    for old, new in _repair_replacements():
        if old not in patched:
            raise AssertionError('Installed confirm_view does not match a serialization replacement')
        patched = patched.replace(old, new, 1)
    return patched


def _repair_replacements():
    return (
        (
            "    @staticmethod\n    def confirm_owned_identity(path, expected, observed):\n",
            "    IDENTITY_REPLY_SEP = '<<AC>>'\n\n    @staticmethod\n    def confirm_owned_identity(path, expected, observed):\n",
        ),
        (
            "            raise NativeError('Unexpected active document expected:'+expected+' observed:'+observed,'native_capture')\n\n    def confirm_view(self, app, path, request):\n",
            "            raise NativeError('Unexpected active document expected:'+expected+' observed:'+observed,'native_capture')\n\n    @staticmethod\n    def parse_identity_reply(result):\n        # Quoted sentinel, not AppleScript tab. Excel's dictionary defines\n        # class tab (Xtab); inside tell Excel that identifier is not ASCII 9.\n        parts = (result or '').split(MacOffice.IDENTITY_REPLY_SEP)\n        if len(parts) != 3:\n            raise NativeError('Active document identity unavailable: malformed identity reply','native_capture')\n        return parts\n\n    def confirm_view(self, app, path, request):\n",
        ),
        (
            "        check += 'set rect to bounds of window 1 of targetDoc\\nreturn expectedId & tab & observedId & tab & (item 1 of rect as text) & \",\" & (item 2 of rect as text) & \",\" & (item 3 of rect as text) & \",\" & (item 4 of rect as text)'\n        result = self.script(app, self.find(app, path, check)+'\\nerror \"Fixed slot is not open\"', *args)\n        parts = result.split('\\t')\n        if len(parts) != 3:\n            raise NativeError('Active document identity unavailable: malformed identity reply','native_capture')\n",
            "        sep = self.IDENTITY_REPLY_SEP\n        check += 'set rect to bounds of window 1 of targetDoc\\nreturn expectedId & \"'+sep+'\" & observedId & \"'+sep+'\" & (item 1 of rect as text) & \",\" & (item 2 of rect as text) & \",\" & (item 3 of rect as text) & \",\" & (item 4 of rect as text)'\n        result = self.script(app, self.find(app, path, check)+'\\nerror \"Fixed slot is not open\"', *args)\n        parts = self.parse_identity_reply(result)\n",
        ),
    )


def load_repaired():
    source = INSTALLED.read_text()
    text = source if "IDENTITY_REPLY_SEP = '<<AC>>'" in source else apply_repair(source)
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name) / 'native_office.py'
    path.write_text(text)
    spec = importlib.util.spec_from_file_location('repaired_native_office', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._keep_tmp = tmp
    return module


def osascript_strip(code, *args):
    result = subprocess.run(
        ['/usr/bin/osascript', '-e', code, '--', *map(str, args)],
        capture_output=True,
        text=True,
        timeout=8,
    )
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip() or 'osascript failed')
    return result.stdout.strip()


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
    def test_installed_runtime_matches_deployed_serialization_repair(self):
        installed = INSTALLED.read_text()
        maintained = MAINTAINED.read_text()
        self.assertEqual(installed, maintained)
        self.assertEqual(sha256(INSTALLED), DEPLOYED_RUNTIME_SHA256)
        self.assertEqual(sha256(MAINTAINED), DEPLOYED_RUNTIME_SHA256)
        self.assertNotEqual(sha256(INSTALLED), LEGACY_TAB_RUNTIME_SHA256)
        self.assertNotIn(DEFECTIVE_SPECIFIER, installed)
        self.assertIn('POSIX path of ((full name of targetDoc) as text)', installed)
        self.assertIn('def confirm_owned_identity', installed)
        self.assertNotIn(DEFECTIVE_TAB_RETURN, installed)
        self.assertNotIn("parts = result.split('\\t')", installed)
        self.assertIn("IDENTITY_REPLY_SEP = '<<AC>>'", installed)
        self.assertIn(DEFECTIVE_SPECIFIER, SPECIFIER_PATCH.read_text())
        self.assertIn(DEFECTIVE_TAB_RETURN, SERIALIZATION_PATCH.read_text())

    def test_deployed_runtime_keeps_specifier_protections(self):
        repaired = INSTALLED.read_text()
        confirm = repaired.split('def confirm_view', 1)[1].split('def capture', 1)[0]
        self.assertNotIn(DEFECTIVE_SPECIFIER, confirm)
        self.assertNotIn(DEFECTIVE_TAB_RETURN, confirm)
        self.assertNotIn("result.split('\\t')", confirm)
        self.assertIn(QUOTED_SENTINEL_RETURN, confirm)
        self.assertIn("IDENTITY_REPLY_SEP = '<<AC>>'", repaired)
        self.assertIn('def parse_identity_reply', repaired)
        self.assertIn('POSIX path of ((full name of targetDoc)', confirm)
        self.assertIn("POSIX path of ((full name of '+active+') as text)", confirm)
        self.assertIn("active = 'active workbook' if app == 'excel' else 'active document'", confirm)
        self.assertIn('Unexpected worksheet', confirm)
        self.assertIn('Unexpected Word selection', confirm)
        self.assertIn('name of active sheet of targetDoc', confirm)
        self.assertIn('selection start of selection of window 1 of targetDoc', confirm)
        self.assertIn('Fixed slot is not open', confirm)
        self.assertIn('def confirm_owned_identity', repaired)
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
        self.sep = self.office.MacOffice.IDENTITY_REPLY_SEP

    def _own(self, app, path):
        self.backend.opened[(app, str(path))] = (self.backend.reference(app, path), ('lock',))

    def _script(self, expected, observed, rect='40,40,800,600', error=None):
        def script(app, body, *args, **kwargs):
            self.bodies.append(body)
            if error:
                raise self.office.NativeError(error, 'native_capture')
            return expected + self.sep + observed + self.sep + rect
        self.backend.script = script

    def test_owned_excel_document_returns_bounds(self):
        self._own('excel', self.slot)
        self._script(str(self.slot), str(self.slot))
        bounds = self.backend.confirm_view('excel', self.slot, {'worksheet': 'Overview'})
        self.assertEqual(bounds, [40, 40, 800, 600])
        body = self.bodies[-1]
        self.assertIn('full name of active workbook', body)
        self.assertNotIn('is not targetDoc', body)
        self.assertNotIn('& tab &', body)
        self.assertIn(f'& "{self.sep}" &', body)
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
        self.assertNotIn('& tab &', body)
        self.assertIn(f'& "{self.sep}" &', body)

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

    def test_tab_separated_legacy_reply_is_not_accepted(self):
        self._own('excel', self.slot)
        self.backend.script = lambda *a, **k: str(self.slot) + '\t' + str(self.slot) + '\t40,40,800,600'
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
        self.sep = self.office.MacOffice.IDENTITY_REPLY_SEP

    def _workspace(self, expected=None, observed=None, drop_ownership=False, identity_error=None, raw_reply=None):
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
            if raw_reply is not None:
                return raw_reply
            path = slot_holder['path']
            exp = str(path) if expected is None else expected
            obs = str(path) if observed is None else observed
            return exp + self.sep + obs + self.sep + '40,40,800,600'

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

    def test_wrong_owned_slot_path_never_reaches_capture(self):
        ws, backend = self._workspace(expected='/tmp/other/excel-view.xlsx', observed='/tmp/other/excel-view.xlsx')
        result = ws.view(self._request())
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertFalse(any(e[0] == 'capture' for e in backend.events))
        self.assertIn('Owned document path mismatch', result['action'])

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

    def test_malformed_reply_never_reaches_capture(self):
        ws, backend = self._workspace(raw_reply='40,40,800,600')
        result = ws.view(self._request())
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertFalse(any(e[0] == 'capture' for e in backend.events))
        self.assertIn('malformed identity reply', result['action'])

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


class TransportTests(unittest.TestCase):
    """Real osascript producer/consumer boundary. No Office tell block."""

    @classmethod
    def setUpClass(cls):
        cls.office = load_repaired()
        cls.sep = cls.office.MacOffice.IDENTITY_REPLY_SEP
        cls.slot = '/tmp/autocycle-office/excel-view.xlsx'
        cls.bounds = '40,40,1320,1000'

    def _return_code(self, join_expr, expected=None, observed=None, rect=None):
        expected = self.slot if expected is None else expected
        observed = self.slot if observed is None else observed
        rect = self.bounds if rect is None else rect
        code = (
            'on run argv\n'
            'set expectedId to item 1 of argv\n'
            'set observedId to item 2 of argv\n'
            'set rectText to item 3 of argv\n'
            'return '+join_expr+'\n'
            'end run'
        )
        return osascript_strip(code, expected, observed, rect)

    def test_unshadowed_tab_survives_osascript_but_repaired_parser_rejects_it(self):
        reply = self._return_code('expectedId & tab & observedId & tab & rectText')
        self.assertEqual(reply.split('\t'), [self.slot, self.slot, self.bounds])
        with self.assertRaises(self.office.NativeError) as raised:
            self.office.MacOffice.parse_identity_reply(reply)
        self.assertIn('malformed identity reply', str(raised.exception))

    def test_excel_xtab_class_reply_is_the_receipt_failure(self):
        reply = self._return_code('expectedId & «class Xtab» & observedId & «class Xtab» & rectText')
        self.assertNotIn('\t', reply)
        self.assertIn('«class Xtab»', reply)
        self.assertEqual(len(reply.split(self.sep)), 1)
        with self.assertRaises(self.office.NativeError) as raised:
            self.office.MacOffice.parse_identity_reply(reply)
        self.assertEqual(str(raised.exception), 'Active document identity unavailable: malformed identity reply')

    def test_quoted_sentinel_survives_osascript_strip_and_parse(self):
        join = 'expectedId & "'+self.sep+'" & observedId & "'+self.sep+'" & rectText'
        reply = self._return_code(join)
        parts = self.office.MacOffice.parse_identity_reply(reply)
        self.assertEqual(parts, [self.slot, self.slot, self.bounds])
        self.office.MacOffice.confirm_owned_identity(self.slot, parts[0], parts[1])
        self.assertEqual([int(float(n)) for n in parts[2].split(',')], [40, 40, 1320, 1000])

    def test_script_wrapper_shape_preserves_sentinel_without_office_tell(self):
        code = (
            'on run argv\n'
            'set slotPath to item 1 of argv\n'
            'with timeout of 12 seconds\n'
            'return slotPath & "'+self.sep+'" & slotPath & "'+self.sep+'" & "40,40,1320,1000"\n'
            'end timeout\n'
            'end run'
        )
        reply = osascript_strip(code, self.slot)
        parts = self.office.MacOffice.parse_identity_reply(reply)
        self.assertEqual(parts[0], self.slot)
        self.assertEqual(parts[1], self.slot)
        self.assertEqual(parts[2], self.bounds)

    def test_missing_malformed_and_ambiguous_replies_fail_closed(self):
        parser = self.office.MacOffice.parse_identity_reply
        cases = (
            '',
            self.bounds,
            self.slot,
            self.slot + self.sep + self.slot,
            self.slot + self.sep + self.slot + self.sep + self.bounds + self.sep + 'extra',
            self.slot + '\t' + self.slot + '\t' + self.bounds,
            self.slot + '«class Xtab»' + self.slot + '«class Xtab»' + self.bounds,
        )
        for reply in cases:
            with self.subTest(reply=reply):
                with self.assertRaises(self.office.NativeError) as raised:
                    parser(reply)
                self.assertIn('malformed identity reply', str(raised.exception))

    def test_confirm_view_uses_real_osascript_transport(self):
        office = load_repaired()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        slot = Path(tmp.name) / 'excel-view.xlsx'
        slot.write_bytes(b'slot')
        backend = office.MacOffice()
        backend.opened[('excel', str(slot))] = (backend.reference('excel', slot), ('lock',))
        backend.is_open = lambda app, path: (app, str(path)) in backend.opened
        bodies = []
        sep = office.MacOffice.IDENTITY_REPLY_SEP

        def script(app, body, *args, **kwargs):
            bodies.append(body)
            self.assertIn(f'& "{sep}" &', body)
            self.assertNotIn('& tab &', body)
            code = (
                'on run argv\n'
                'return (item 1 of argv) & "'+sep+'" & (item 2 of argv) & "'+sep+'" & (item 3 of argv)\n'
                'end run'
            )
            return osascript_strip(code, str(slot), str(slot), '40,40,1320,1000')

        backend.script = script
        bounds = backend.confirm_view('excel', slot, {'worksheet': 'Overview'})
        self.assertEqual(bounds, [40, 40, 1320, 1000])
        self.assertTrue(bodies)

    def test_confirm_view_transport_rejects_xtab_and_blocks_capture(self):
        office = load_repaired()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        source = root / 'source.xlsx'
        source.write_bytes(b'authoritative')
        backend = office.MacOffice()
        events = []

        def open_slot(app, path):
            backend.opened[(app, str(path))] = (backend.reference(app, path), ('lock',))

        def script(app, body, *args, **kwargs):
            events.append(('script', body))
            code = (
                'on run argv\n'
                'return (item 1 of argv) & «class Xtab» & (item 1 of argv) & «class Xtab» & "40,40,1320,1000"\n'
                'end run'
            )
            return osascript_strip(code, '/tmp/autocycle-office/excel-view.xlsx')

        def capture(path, bounds):
            events.append(('capture', path, bounds))
            png(path)

        backend.open = open_slot
        backend.close = lambda app, path, save: backend.opened.pop((app, str(path)), None)
        backend.is_open = lambda app, path: (app, str(path)) in backend.opened
        backend.script = script
        backend.position = lambda app, path, request: [40, 40, 1320, 1000]
        backend.capture = capture
        backend.frontmost = lambda: ''
        backend.restore = lambda bundle: None
        ws = office.Workspace(root / '.git' / 'autocycle', backend, wait_seconds=.01, poll_seconds=.001)
        result = ws.view({
            'app': 'excel',
            'source': str(source),
            'source_sha256': office.digest(source),
            'worksheet': 'Overview',
        })
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertFalse(any(e[0] == 'capture' for e in events))
        self.assertIn('malformed identity reply', result['action'])

    def test_same_name_different_path_fails_after_real_transport(self):
        office = load_repaired()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        slot = Path(tmp.name) / 'excel-view.xlsx'
        slot.write_bytes(b'slot')
        decoy = '/tmp/other/excel-view.xlsx'
        backend = office.MacOffice()
        backend.opened[('excel', str(slot))] = (backend.reference('excel', slot), ('lock',))
        backend.is_open = lambda app, path: (app, str(path)) in backend.opened
        sep = office.MacOffice.IDENTITY_REPLY_SEP

        def script(app, body, *args, **kwargs):
            code = (
                'on run argv\n'
                'return (item 1 of argv) & "'+sep+'" & (item 2 of argv) & "'+sep+'" & (item 3 of argv)\n'
                'end run'
            )
            return osascript_strip(code, str(slot), decoy, '40,40,1320,1000')

        backend.script = script
        with self.assertRaises(office.NativeError) as raised:
            backend.confirm_view('excel', slot, {'worksheet': 'Overview'})
        self.assertIn(decoy, str(raised.exception))


if __name__ == '__main__':
    unittest.main()
