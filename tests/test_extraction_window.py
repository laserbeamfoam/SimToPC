from pathlib import Path


RESOURCE_DIR = Path(__file__).resolve().parents[1] / "simtopc" / "resources" / "src"
EXTRACTION_SCRIPTS = (
    "extract_meltpool.py",
    "extract_x_z_slice_meltpool.py",
    "extract_y_z_slice_meltpool.py",
)


def test_extraction_uses_configured_y_window_without_implicit_spot_trim():
    for script_name in EXTRACTION_SCRIPTS:
        source = (RESOURCE_DIR / script_name).read_text(encoding="utf-8")

        assert "Y_COORD_BEGIN_TRACK + parameters" not in source
        assert "Y_COORD_END_TRACK - parameters" not in source
        assert "Y_COORD_BEGIN_TRACK, 7.499999628635123e-05" in source
        assert "Y_COORD_END_TRACK, 7.375000132014975e-05" in source
