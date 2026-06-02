from pathlib import Path


def test_shell_viewer_installs_quaternion_inverse_compatibility_shim():
    shell_viewer = Path("static/js/components/shell-viewer.js").read_text(encoding="utf-8")
    assert "Quaternion.inverse compatibility shim" in shell_viewer
    assert "ensureThreeCompatibility" in shell_viewer
    assert "setResourcePath" in shell_viewer
    assert "fallback OBJ load failed" in shell_viewer
    assert "invalidateModelLoad" in shell_viewer
    assert "invalidateTextureLoad" in shell_viewer
    assert "disposeObject3D" in shell_viewer
    assert "prepareShellObject" in shell_viewer
    assert "clearLoadingState" in shell_viewer
    assert "updateFloatMotion" in shell_viewer
    assert "getShellMaterialProfile" in shell_viewer
    assert "createShellMaterialMap" in shell_viewer
    assert "applyShellAppearance" in shell_viewer
    assert "text/uri-list" in shell_viewer
    assert "style.display = 'flex'" in shell_viewer
    assert "Failed to load shell materials" not in shell_viewer
    assert "Using fallback model" not in shell_viewer
    assert "MeshPhysicalMaterial" in shell_viewer
    assert "MeshBasicMaterial" not in shell_viewer
    assert "this.currentTextureUrl = null;" in shell_viewer
    assert "this.pendingTextureUrl = null;" in shell_viewer


def test_orbit_controls_supports_inverse_and_invert():
    orbit_controls = Path("static/vendor/three/examples/js/controls/OrbitControls.js").read_text(encoding="utf-8")
    assert "quat.clone().invert()" in orbit_controls or "quat.clone().inverse()" in orbit_controls


def test_pattern_pages_do_not_auto_apply_generated_texture():
    page_212 = Path("static/js/activator_212.js").read_text(encoding="utf-8")
    page_23 = Path("static/js/activator_23.js").read_text(encoding="utf-8")

    assert "this.viewer.applyTexture(imageUrl)" not in page_212
    assert "this.viewer.applyTexture(imageUrl)" not in page_23
    assert "if (this.currentImageUrl) {\n                this.viewer.applyTexture(this.currentImageUrl);" not in page_212
    assert "if (this.currentImageUrl) {\n                this.viewer.applyTexture(this.currentImageUrl);" not in page_23
    assert "this.viewer.resetTexture();" in page_212
    assert "this.viewer.resetTexture();" in page_23
    assert "dragstart" in page_212
    assert "dragstart" in page_23
