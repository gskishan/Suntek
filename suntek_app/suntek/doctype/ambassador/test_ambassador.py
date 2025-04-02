import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from .tests.create_ambassador import (
    create_ambassador_with_invalid_aadhar,
    create_ambassador_with_invalid_pan,
    create_valid_ambassador,
)


class TestAmbassador(FrappeTestCase):
    def tearDown(self):
        try:
            frappe.db.delete("Ambassador", {"name": self.ambassador_name})
            frappe.db.commit()
        except Exception:
            frappe.db.rollback()

    def test_ambassador_creation(self):
        ambassador = create_valid_ambassador()
        self.assertEqual(ambassador.ambassador_name, "Test Ambassador")

    def test_ambassador_creation_with_invalid_pan(self):
        with self.assertRaises(ValidationError) as context:
            create_ambassador_with_invalid_pan()

        self.assertIn("Invalid PAN Number Format", str(context.exception))

    def test_ambassador_creation_with_invalid_aadhar(self):
        with self.assertRaises(ValidationError) as context:
            create_ambassador_with_invalid_aadhar()

        self.assertIn("Aadhar Number must be 12 digits", str(context.exception))
