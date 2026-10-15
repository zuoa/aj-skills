import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/fetch_district_geojson.py'
spec = importlib.util.spec_from_file_location('district_import', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def response(polyline='120,30;121,30;121,31;120,31', **district):
    return {'status': '1', 'infocode': '10000', 'districts': [{'adcode': '310101', 'name': '示例区', 'level': 'district', 'polyline': polyline, **district}]}


class DistrictImportTests(unittest.TestCase):
    def test_closes_ring_and_keeps_gcj_metadata_and_id(self):
        geo = module.convert_response(response(), '310101')
        self.assertEqual(geo['coordinateSystem'], 'GCJ02')
        f = geo['features'][0]
        self.assertEqual(f['properties']['adcode'], '310101')
        self.assertEqual(f['geometry']['coordinates'][0][0], f['geometry']['coordinates'][0][-1])

    def test_detached_polygons_and_holes(self):
        polyline = '120,30;124,30;124,34;120,34|121,31;122,31;122,32;121,32|125,30;126,30;126,31;125,31'
        geom = module.parse_polyline(polyline)
        self.assertEqual(geom['type'], 'MultiPolygon')
        self.assertEqual([len(p) for p in geom['coordinates']], [2, 1])

    def test_ambiguous_name_requires_adcode(self):
        raw = response(); raw['districts'].append({**raw['districts'][0], 'adcode': '310102'})
        with self.assertRaisesRegex(ValueError, '歧义'):
            module.convert_response(raw, '示例区')
        self.assertEqual(module.convert_response(raw, '示例区', '310102')['features'][0]['properties']['adcode'], '310102')

    def test_no_street_boundary_is_not_fabricated(self):
        with self.assertRaisesRegex(ValueError, '没有边界'):
            module.convert_response(response('', level='street'), '示例区')

    def test_wrong_adcode_and_api_failure(self):
        with self.assertRaises(ValueError):
            module.convert_response(response(), '示例区', '999999')
        with self.assertRaisesRegex(ValueError, '10001'):
            module.convert_response({'status':'0','infocode':'10001','info':'secret_key'}, '示例区')

    def test_invalid_coordinates_are_rejected(self):
        for text in ['nan,30;121,30;121,31', '120,30;120,30;120,30', 'garbage', '180,90;181,90;180,91']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                module.parse_polyline(text)

    def test_offline_cli_and_no_implicit_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp); source = folder/'response.json'; output = folder/'district.geo.json'
            source.write_text(json.dumps(response()))
            cmd = [sys.executable, str(SCRIPT), '--keywords', '310101', '--response-json', str(source), '--output', str(output)]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(output.read_text())['coordinateSystem'], 'GCJ02')
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn('已存在', second.stderr)

    def test_missing_key_cli_has_actionable_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {k:v for k,v in os.environ.items() if k != 'AMAP_WEB_SERVICE_KEY'}
            result = subprocess.run([sys.executable, str(SCRIPT), '--keywords', '310101', '--output', str(Path(tmp)/'out.json')], env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('AMAP_WEB_SERVICE_KEY', result.stderr)


if __name__ == '__main__':
    unittest.main()
