import pytest


def test_direct_upload_success(page, tmp_path):
    test_file = tmp_path / "repor.pdf"
    test_file.write_bytes(b"%PDF-1.4 test content")
    
    page.locator('[data-testid="stFileUploaderDropzone"] input[type="file"]').set_input_files(str(test_file))
    page.wait_for_load_state("networkidle")
    
    page.get_by_role("button", name="Upload").click()
    page.wait_for_load_state("networkidle")
    
    assert page.get_by_text("Uploaded!").is_visible()

def test_upload_no_file_shows_no_button(page):
    # Button should not be visible without a file selected
    assert not page.get_by_role("button", name="Upload").is_visible()

def test_custom_upload_flow(page, tmp_path):
    test_file = tmp_path / "expenses.xlsx"
    test_file.write_bytes(b"fake xlsx content")

    page.get_by_label("Customize name / ype before saving").check()
    page.locator('[data-testid="stFileUploaderDropzone"] input[type="file"]').set_input_files(str(test_file))
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="Upload").click()
    page.wait_for_load_state("networkidle")

    # Preview form should appear
    assert page.get_by_label("File Name").is_visible()

    page.get_by_label("File Name").fill("Q1 Report")
    page.get_by_role("button", name="Confirm Upload").click()
    page.wait_for_load_state("networkidle")

    assert page.get_by_text("Uploaded!").is_visible()