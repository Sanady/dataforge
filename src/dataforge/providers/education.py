"""EducationProvider — generates fake education-related data.

Includes university names, degree types, and fields of study.
All data is stored as immutable ``tuple[str, ...]``.
"""

from typing import Literal, overload

from dataforge.providers.base import BaseProvider

# ------------------------------------------------------------------
# Data tuples (immutable, module-level)
# ------------------------------------------------------------------

_UNIVERSITIES: tuple[str, ...] = (
    "Harvard University",
    "Stanford University",
    "MIT",
    "University of Cambridge",
    "University of Oxford",
    "California Institute of Technology",
    "Princeton University",
    "Yale University",
    "Columbia University",
    "University of Chicago",
    "Duke University",
    "University of Pennsylvania",
    "Johns Hopkins University",
    "Northwestern University",
    "Cornell University",
    "University of Michigan",
    "University of California, Berkeley",
    "UCLA",
    "University of Virginia",
    "Georgetown University",
    "Carnegie Mellon University",
    "New York University",
    "University of Southern California",
    "Boston University",
    "University of Wisconsin-Madison",
    "University of Texas at Austin",
    "Georgia Institute of Technology",
    "University of Washington",
    "University of Illinois Urbana-Champaign",
    "Purdue University",
    "University of Minnesota",
    "Ohio State University",
    "Penn State University",
    "University of Florida",
    "University of North Carolina at Chapel Hill",
    "University of Maryland",
    "Indiana University",
    "Arizona State University",
    "University of Colorado Boulder",
    "Michigan State University",
    "University of Oregon",
    "Vanderbilt University",
    "Rice University",
    "Emory University",
    "Washington University in St. Louis",
    "Tufts University",
    "Brown University",
    "Dartmouth College",
    "University of Notre Dame",
    "University of Rochester",
)

_DEGREES: tuple[str, ...] = (
    "Associate of Arts",
    "Associate of Science",
    "Bachelor of Arts",
    "Bachelor of Science",
    "Bachelor of Fine Arts",
    "Bachelor of Engineering",
    "Master of Arts",
    "Master of Science",
    "Master of Business Administration",
    "Master of Fine Arts",
    "Master of Engineering",
    "Master of Education",
    "Master of Public Health",
    "Master of Social Work",
    "Doctor of Philosophy",
    "Doctor of Medicine",
    "Doctor of Education",
    "Juris Doctor",
    "Doctor of Dental Surgery",
    "Doctor of Veterinary Medicine",
)

_FIELDS_OF_STUDY: tuple[str, ...] = (
    "Computer Science",
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Engineering",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Biomedical Engineering",
    "Economics",
    "Business Administration",
    "Finance",
    "Accounting",
    "Marketing",
    "Management",
    "Psychology",
    "Sociology",
    "Political Science",
    "History",
    "English Literature",
    "Philosophy",
    "Art History",
    "Music",
    "Theater",
    "Nursing",
    "Public Health",
    "Medicine",
    "Law",
    "Education",
    "Architecture",
    "Environmental Science",
    "Geology",
    "Astronomy",
    "Linguistics",
    "Anthropology",
    "Communications",
    "Journalism",
    "Information Technology",
    "Data Science",
    "Statistics",
    "Neuroscience",
    "International Relations",
    "Criminal Justice",
    "Social Work",
    "Graphic Design",
    "Film Studies",
    "Pharmacology",
    "Biochemistry",
)


class EducationProvider(BaseProvider):
    """Generates fake education-related data.

    This provider is locale-independent.

    Parameters
    ----------
    engine : RandomEngine
        The shared random engine instance.
    """

    __slots__ = ()

    _provider_name = "education"
    _locale_modules: tuple[str, ...] = ()
    _field_map: dict[str, str] = {
        "university": "university",
        "degree": "degree",
        "field_of_study": "field_of_study",
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @overload
    def university(self) -> str: ...
    @overload
    def university(self, count: Literal[1]) -> str: ...
    @overload
    def university(self, count: int) -> str | list[str]: ...
    def university(self, count: int = 1) -> str | list[str]:
        """Generate a university name (e.g. ``"Stanford University"``).

        Parameters
        ----------
        count : int
            Number of university names to generate.

        Returns
        -------
        str or list[str]
        """
        if count == 1:
            return self._engine.choice(_UNIVERSITIES)
        return self._engine.choices(_UNIVERSITIES, count)

    @overload
    def degree(self) -> str: ...
    @overload
    def degree(self, count: Literal[1]) -> str: ...
    @overload
    def degree(self, count: int) -> str | list[str]: ...
    def degree(self, count: int = 1) -> str | list[str]:
        """Generate a degree type (e.g. ``"Bachelor of Science"``).

        Parameters
        ----------
        count : int
            Number of degrees to generate.

        Returns
        -------
        str or list[str]
        """
        if count == 1:
            return self._engine.choice(_DEGREES)
        return self._engine.choices(_DEGREES, count)

    @overload
    def field_of_study(self) -> str: ...
    @overload
    def field_of_study(self, count: Literal[1]) -> str: ...
    @overload
    def field_of_study(self, count: int) -> str | list[str]: ...
    def field_of_study(self, count: int = 1) -> str | list[str]:
        """Generate a field of study (e.g. ``"Computer Science"``).

        Parameters
        ----------
        count : int
            Number of fields to generate.

        Returns
        -------
        str or list[str]
        """
        if count == 1:
            return self._engine.choice(_FIELDS_OF_STUDY)
        return self._engine.choices(_FIELDS_OF_STUDY, count)
