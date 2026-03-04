"""Tests for the GovernmentProvider."""

import re

from dataforge import DataForge


class TestGovernmentSSN:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_ssn_format(self) -> None:
        ssn = self.forge.government.ssn()
        assert re.match(r"^\d{3}-\d{2}-\d{4}$", ssn)

    def test_ssn_no_666_area(self) -> None:
        for _ in range(1000):
            ssn = self.forge.government.ssn()
            area = int(ssn.split("-")[0])
            assert area != 666
            assert 1 <= area <= 899

    def test_ssn_batch(self) -> None:
        results = self.forge.government.ssn(count=100)
        assert isinstance(results, list)
        assert len(results) == 100
        for ssn in results:
            assert re.match(r"^\d{3}-\d{2}-\d{4}$", ssn)


class TestGovernmentTaxId:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_tax_id_format(self) -> None:
        tid = self.forge.government.tax_id()
        assert re.match(r"^\d{2}-\d{7}$", tid)

    def test_tax_id_batch(self) -> None:
        results = self.forge.government.tax_id(count=50)
        assert len(results) == 50
        for tid in results:
            assert re.match(r"^\d{2}-\d{7}$", tid)


class TestGovernmentPassport:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_passport_format(self) -> None:
        pp = self.forge.government.passport_number()
        assert re.match(r"^[A-Z]\d{8}$", pp)

    def test_passport_batch(self) -> None:
        results = self.forge.government.passport_number(count=50)
        assert len(results) == 50
        for pp in results:
            assert re.match(r"^[A-Z]\d{8}$", pp)


class TestGovernmentDriversLicense:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_drivers_license_format(self) -> None:
        dl = self.forge.government.drivers_license()
        assert re.match(r"^[A-Z]\d{7}$", dl)

    def test_drivers_license_batch(self) -> None:
        results = self.forge.government.drivers_license(count=50)
        assert len(results) == 50


class TestGovernmentNationalId:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_national_id_format(self) -> None:
        nid = self.forge.government.national_id()
        assert re.match(r"^\d{10}$", nid)

    def test_national_id_batch(self) -> None:
        results = self.forge.government.national_id(count=50)
        assert len(results) == 50
        for nid in results:
            assert re.match(r"^\d{10}$", nid)


class TestGovernmentInSchema:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_schema_ssn(self) -> None:
        rows = self.forge.to_dict(fields=["ssn", "first_name"], count=5)
        assert len(rows) == 5
        for row in rows:
            assert "ssn" in row
            assert re.match(r"^\d{3}-\d{2}-\d{4}$", row["ssn"])
