import bids
import pandas as pd

import SnakeMaker.defaults as df


class SubjectSession:
    def __init__(self, data: pd.DataFrame, session_id: str) -> None:
        # Parameters
        self.t1 = None
        self.b0 = None
        self.b1000 = None
        self.session_id = None
        # Initialize parameters
        self.session_id = session_id
        self.populate(data)

    def populate(self, data: pd.DataFrame, config: dict = df.t1) -> None:
        # Parse data for each input
        t1_data = data[data["datatype"] == config["datatype"]]
        self.t1 = self.populate_t1(
            nifti_path=t1_data[t1_data["extension"].isin([".nii.gz", ".nii"])].values[0][0],
            json_path=t1_data[t1_data["extension"] == ".json"].values[0][0],
        )
        # Populate b0
        b0_data = data[data["acquisition"] == "b0"]
        self.b0 = self.populate_b0(
            nifti_path=b0_data[b0_data["extension"].isin([".nii.gz", ".nii"])].values[0][0],
            json_path=b0_data[b0_data["extension"] == ".json"].values[0][0],
            bvals_path=b0_data[b0_data["extension"] == ".bval"].values[0][0],
            bvecs_path=b0_data[b0_data["extension"] == ".bvec"].values[0][0],
            direction=b0_data["direction"].values[0] if "direction" in b0_data.columns and isinstance(b0_data["direction"].values[0], str) else "",
        )
        # Populate b1000
        b1000_data = data[data["acquisition"] == "b1000"]
        self.b1000 = self.populate_b1000(
            nifti_path=b1000_data[b1000_data["extension"].isin([".nii.gz", ".nii"])].values[0][0],
            json_path=b1000_data[b1000_data["extension"] == ".json"].values[0][0],
            bvals_path=b1000_data[b1000_data["extension"] == ".bval"].values[0][0],
            bvecs_path=b1000_data[b1000_data["extension"] == ".bvec"].values[0][0],
            direction=b1000_data["direction"].values[0]
            if "direction" in b1000_data.columns and isinstance(b1000_data["direction"].values[0], str)
            else "",
        )

    def populate_b0(self, nifti_path: str, json_path: str, bvals_path: str, bvecs_path: str, direction: str = "", config: dict = df.b0) -> None:
        self.b0 = config
        self.b0["nifti"] = nifti_path
        self.b0["json"] = json_path
        self.b0["bval"] = bvals_path
        self.b0["bvec"] = bvecs_path
        self.b0["direction"] = direction
        return self.b0

    def populate_b1000(self, nifti_path: str, json_path: str, bvals_path: str, bvecs_path: str, direction: str = "", config: dict = df.b0) -> None:
        self.b0 = config
        self.b0["nifti"] = nifti_path
        self.b0["json"] = json_path
        self.b0["bval"] = bvals_path
        self.b0["bvec"] = bvecs_path
        self.b0["direction"] = direction
        return self.b0

    def populate_t1(self, nifti_path, json_path, config: dict = df.t1) -> pd.DataFrame:
        self.t1 = config
        self.t1["nifti"] = nifti_path
        self.t1["json"] = json_path
        return self.t1


class Subject:
    def __init__(self, subject_id: str, subject_data: pd.DataFrame) -> None:
        # Parameters
        self.subject_id = str()
        self.sessions = dict()
        self.data = None
        # Initialize parameters
        self.subject_id = subject_id
        self.data = self.populate(subject_data)

    def populate(self, data: pd.DataFrame) -> None:
        """
        Populates the subject's sessions based on the provided data.

        Args:
            data (pd.DataFrame): The data containing information about the subject's sessions.

        Returns:
            None
        """
        for session_id in data[(data["subject"] == self.subject_id)]["session"].unique():  # For each session
            subdf = data[(data["subject"] == self.subject_id) & (data["session"] == str(session_id))]
            self.sessions[session_id] = SubjectSession(subdf, session_id)

    def get_sessions_number(self) -> int:
        """
        Returns the number of sessions for the subject.

        Returns:
            int: The number of sessions.
        """
        return len(self.sessions)

    def get_session_by_id(self, session_id: str) -> SubjectSession:
        """
        Retrieve a SubjectSession object by its session ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            SubjectSession: The SubjectSession object corresponding to the given session ID.
        """
        return self.sessions[session_id]

    def get_file(self, session_id: str, data: str, attribut: str) -> str:
        """
        Retrieves the value of a specific attribute from the data dictionary of a session.

        Args:
            session_id (str): The ID of the session.
            data (str): The key of the data dictionary.
            attribut (str): The attribute to retrieve from the data dictionary. (commonly nifti, json, bval, bvec, etc.)

        Returns:
            str: The value of the specified attribute.

        Raises:
            KeyError: If the session ID or data key is not found.
        """
        return self.sessions[session_id].__dict__[data][attribut]
