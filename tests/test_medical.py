"""Tests for the MedicalProvider."""

import re

from dataforge import DataForge


class TestMedicalBloodType:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_blood_type_valid(self) -> None:
        valid = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
        for _ in range(100):
            bt = self.forge.medical.blood_type()
            assert bt in valid

    def test_blood_type_batch(self) -> None:
        results = self.forge.medical.blood_type(count=50)
        assert len(results) == 50


class TestMedicalICD10:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_icd10_format(self) -> None:
        code = self.forge.medical.icd10_code()
        assert re.match(r"^[A-T]\d{2}\.\d$", code)

    def test_icd10_batch(self) -> None:
        results = self.forge.medical.icd10_code(count=100)
        assert len(results) == 100
        for code in results:
            assert re.match(r"^[A-T]\d{2}\.\d$", code)


class TestMedicalDrug:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_drug_name(self) -> None:
        name = self.forge.medical.drug_name()
        assert isinstance(name, str)
        assert len(name) > 0

    def test_drug_name_batch(self) -> None:
        results = self.forge.medical.drug_name(count=50)
        assert len(results) == 50

    def test_drug_form(self) -> None:
        form = self.forge.medical.drug_form()
        assert isinstance(form, str)
        assert len(form) > 0

    def test_dosage_format(self) -> None:
        dosage = self.forge.medical.dosage()
        assert isinstance(dosage, str)
        parts = dosage.split(" ")
        assert len(parts) == 2
        assert parts[0].isdigit()


class TestMedicalDiagnosis:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_diagnosis(self) -> None:
        diag = self.forge.medical.diagnosis()
        assert isinstance(diag, str)
        assert len(diag) > 0

    def test_diagnosis_batch(self) -> None:
        results = self.forge.medical.diagnosis(count=50)
        assert len(results) == 50


class TestMedicalProcedure:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_procedure(self) -> None:
        proc = self.forge.medical.procedure()
        assert isinstance(proc, str)
        assert len(proc) > 0

    def test_procedure_batch(self) -> None:
        results = self.forge.medical.procedure(count=50)
        assert len(results) == 50


class TestMedicalMRN:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_mrn_format(self) -> None:
        mrn = self.forge.medical.medical_record_number()
        assert mrn.startswith("MRN-")
        assert re.match(r"^MRN-\d{8}$", mrn)

    def test_mrn_batch(self) -> None:
        results = self.forge.medical.medical_record_number(count=50)
        assert len(results) == 50
        for mrn in results:
            assert re.match(r"^MRN-\d{8}$", mrn)


class TestMedicalInSchema:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_schema_fields(self) -> None:
        rows = self.forge.to_dict(
            fields=["blood_type", "drug_name", "diagnosis"], count=5
        )
        assert len(rows) == 5
        for row in rows:
            assert "blood_type" in row
            assert "drug_name" in row
            assert "diagnosis" in row
