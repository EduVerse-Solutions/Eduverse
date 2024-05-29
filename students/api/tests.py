from copy import deepcopy
from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.api import utils
from core.models import User
from students.api.dummy_data import all_guardians_data, all_students_data
from students.models import Student


class StudentViewSetTest(APITestCase):
    """
    Test case for the StudentViewSet class.
    """

    def setUp(self):
        """
        Set up the test case by creating a super admin user and authenticating
        the client.
        """
        self.admin1 = utils.create_super_admin(assign_institution=True)
        self.client.force_authenticate(user=self.admin1)
        admin2_data = {
            "username": "susan_collins23",
            "first_name": "Susan",
            "last_name": "Collins",
            "email": "greenemichael@example.org",
            "date_of_birth": date.fromisoformat("1987-02-10"),
            "address": "66351 Glenn Mount Apt. 765",
            "sex": "F",
        }
        self.admin2 = utils.create_super_admin(**admin2_data)
        self.students_data = deepcopy(all_students_data)
        self.guardians_data = deepcopy(all_guardians_data)

    def test_list_students(self):
        """
        Test the list students API endpoint.
        """
        url = reverse("students:student-list")

        for data in self.students_data:
            data["user"]["institution"] = self.admin1.institution.id
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get("results")), len(all_students_data)
        )
        # verify that the data returned is the same as the data posted
        for i, student in enumerate(response.data.get("results")):
            self.assertEqual(
                student.get("user").get("username"),
                all_students_data[i].get("user").get("username"),
            )
            self.assertEqual(
                student.get("admission_number"),
                all_students_data[i].get("admission_number"),
            )
            self.assertEqual(
                student.get("date_of_admission"),
                all_students_data[i].get("date_of_admission"),
            )
            self.assertEqual(
                student.get("date_of_graduation"),
                all_students_data[i].get("date_of_graduation"),
            )

    def test_list_students_without_institution_admin(self):
        """
        Test the list students API endpoint with an administrator without an
        institution.
        """
        url = reverse("students:student-list")
        self.client.force_authenticate(user=self.admin2)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 0)

    def test_retrieve_student(self):
        """
        Test the retrieve student API endpoint.
        """
        # create two students and retrieve their data test to confirm they are
        # the same
        url = reverse("students:student-list")
        for data in self.students_data:
            data["user"]["institution"] = self.admin1.institution.id
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now retrieve the data of the first student
        response = self.client.get(
            reverse("students:student-detail", args=[1])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("user").get("username"),
            self.students_data[0].get("user").get("username"),
        )

    def test_retrieve_student_with_admin_without_institution(self):
        """
        Test the retrieve student API endpoint with an administrator without an
        institution.
        """
        url = reverse("students:student-list")
        # create the students using the admin with an institution
        for data in self.students_data:
            data["user"]["institution"] = self.admin1.institution.id
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now try accessing any of the students created by the admin who
        # belongs to no institution
        self.client.force_authenticate(user=self.admin2)
        response = self.client.get(
            reverse("students:student-detail", args=[1])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_student(self):
        """
        Test the create student API endpoint.
        """
        url = reverse("students:student-list")
        for data in self.students_data:
            data["user"]["institution"] = self.admin1.institution.id
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_student_without_institution(self):
        """
        Test the create student API endpoint without an institution.
        """
        url = reverse("students:student-list")
        for data in self.students_data:
            response = self.client.post(url, data, format="json")
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST
            )

    def test_create_student_with_invalid_institution(self):
        """
        Test the create student API endpoint with an invalid institution.
        """
        url = reverse("students:student-list")
        for data in self.students_data:
            data["user"]["institution"] = 100
            response = self.client.post(url, data, format="json")
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST
            )

    def test_create_user_with_future_date_of_birth(self):
        """
        Test the create student API endpoint with a future date of birth.
        """
        admission_date = date.today().replace(year=date.today().year + 5)
        url = reverse("students:student-list")
        for data in self.students_data:
            data["user"]["date_of_birth"] = admission_date.isoformat()
            data["user"]["institution"] = self.admin1.institution.id
            response = self.client.post(url, data, format="json")
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST
            )

    def test_create_student_with_admission_date_after_graduation_date(self):
        """
        Test the create student API endpoint with an admission date after the
        graduation date.
        """
        url = reverse("students:student-list")
        for data in self.students_data:
            data["date_of_graduation"] = data["date_of_admission"]
            data["date_of_admission"] = "2027-05-01"
            data["user"]["institution"] = self.admin1.institution.id
            response = self.client.post(url, data, format="json")
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST
            )

    def test_create_student_with_invalid_admission_date(self):
        """
        Test the create student API endpoint with an invalid admission date.
        """
        url = reverse("students:student-list")
        for data in self.students_data:
            data["date_of_admission"] = "2027-13-01"
            data["user"]["institution"] = self.admin1.institution.id
            response = self.client.post(url, data, format="json")
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST
            )

    def test_create_student_with_invalid_graduation_date(self):
        """
        Test the create student API endpoint with an invalid graduation date.
        """
        url = reverse("students:student-list")
        for data in self.students_data:
            data["date_of_graduation"] = "2027-13-01"
            data["user"]["institution"] = self.admin1.institution.id
            response = self.client.post(url, data, format="json")
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST
            )

    def test_create_student_with_invalid_date_format(self):
        """
        Test the create student API endpoint with an invalid date format.
        """
        url = reverse("students:student-list")
        for data in self.students_data:
            data["date_of_graduation"] = "2027-05-01T00:00:00"
            data["user"]["institution"] = self.admin1.institution.id
            response = self.client.post(url, data, format="json")
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST
            )

    def test_create_with_admission_date_earlier_than_date_of_birth(self):
        """
        Test the create student API endpoint with an admission date earlier than
        the date of birth.
        """
        url = reverse("students:student-list")
        for data in self.students_data:
            data["user"]["date_of_birth"] = "2027-05-01"
            data["date_of_admission"] = "1967-05-01"
            data["user"]["institution"] = self.admin1.institution.id
            response = self.client.post(url, data, format="json")
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST
            )

    def test_partial_update_student(self):
        """
        Test the update student API endpoint.
        """
        # create one student
        url = reverse("students:student-list")
        student_data = self.students_data[0]
        student_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(url, student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now update the student with PUT request to the API
        student_data["admission_number"] = "1234"
        student_data["date_of_admission"] = "2021-05-01"
        student_data["date_of_graduation"] = "2025-10-11"
        response = self.client.patch(
            reverse("students:student-detail", args=[1]),
            student_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("admission_number"),
            student_data["admission_number"],
        )

    def test_put_update_student(self):
        """
        Test the update student API endpoint.
        """
        # create one student
        url = reverse("students:student-list")
        student_data = self.students_data[0]
        student_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(url, student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now let's update the student a complete update
        student_data = self.students_data[1]
        response = self.client.put(
            reverse("students:student-detail", args=[1]),
            student_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("admission_number"),
            self.students_data[1]["admission_number"],
        )

    def test_update_student_with_guardian(self):
        """
        Test the update student API endpoint with a guardian.
        """
        # create one student
        url = reverse("students:student-list")
        student_data = self.students_data[0]
        student_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(url, student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        student_response_data = response.data

        # create a guardian
        guardian_data = self.guardians_data[0]
        guardian_data["user"]["institution"] = self.admin1.institution.id
        guardian_data["wards"].append(student_response_data.get("id"))
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        guardian_response_data = response.data

        response = self.client.get(
            reverse(
                "students:student-detail",
                args=[student_response_data.get("id")],
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("guardian"), guardian_response_data.get("id")
        )

    def test_delete_student(self):
        """
        Test the delete student API endpoint.
        """
        # create one student
        url = reverse("students:student-list")
        student_data = self.students_data[0]
        student_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(url, student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 3)  # admins and student

        # now delete the student
        response = self.client.delete(
            reverse("students:student-detail", args=[1])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # ensure the user object was deleted as well
        self.assertEqual(User.objects.count(), 2)  # only admins are left
        self.assertEqual(Student.objects.count(), 0)


class GuardianViewSetTest(APITestCase):
    """
    Test case for the GuardianViewSet class
    """

    def setUp(self):
        """
        Set up the test case by creating a super admin user and authenticating
        the client.
        """
        self.admin1 = utils.create_super_admin(assign_institution=True)
        self.client.force_authenticate(user=self.admin1)
        admin2_data = {
            "username": "susan_collins23",
            "first_name": "Susan",
            "last_name": "Collins",
            "email": "greenemichael@example.org",
            "date_of_birth": date.fromisoformat("1987-02-10"),
            "address": "66351 Glenn Mount Apt. 765",
            "sex": "F",
        }
        self.admin2 = utils.create_super_admin(**admin2_data)
        self.students_data = deepcopy(all_students_data)
        self.guardians_data = deepcopy(all_guardians_data)

    def test_list_guardians(self):
        """
        Test the list guardians API endpoint.
        """
        url = reverse("students:guardian-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 0)

        # create one student
        url = reverse("students:student-list")
        student_data = self.students_data[0]
        student_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(url, student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        student_response_data = response.data

        # create a guardian
        guardian_data = self.guardians_data[0]
        guardian_data["user"]["institution"] = self.admin1.institution.id
        guardian_data["wards"].append(student_response_data.get("id"))
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        guardian_response_data = response.data

        response = self.client.get(
            reverse(
                "students:student-detail",
                args=[student_response_data.get("id")],
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("guardian"), guardian_response_data.get("id")
        )

    def test_retrieve_guardian(self):
        """
        Test the retrieve guardian API endpoint.
        """
        url = reverse("students:guardian-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 0)

        # create one student
        url = reverse("students:student-list")
        student_data = self.students_data[0]
        student_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(url, student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        student_response_data = response.data

        # create a guardian
        guardian_data = self.guardians_data[0]
        guardian_data["user"]["institution"] = self.admin1.institution.id
        guardian_data["wards"].append(student_response_data.get("id"))
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        guardian_response_data = response.data

        # now retrieve the guardian data
        response = self.client.get(
            reverse(
                "students:guardian-detail",
                args=[guardian_response_data.get("id")],
            )
        )

    def test_create_guardian_without_student(self):
        """
        Test the create guardian API endpoint without a student.
        """
        guardian_data = self.guardians_data[0]
        guardian_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_guardian_with_invalid_student(self):
        """
        Test the create guardian API endpoint with an invalid student.
        """
        guardian_data = self.guardians_data[0]
        guardian_data["user"]["institution"] = self.admin1.institution.id
        guardian_data["wards"].append(100)
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_guardian_with_invalid_institution(self):
        """
        Test the create guardian API endpoint with an invalid institution.
        """
        guardian_data = self.guardians_data[0]
        guardian_data["user"]["institution"] = 100
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_guardian_with_future_date_of_birth(self):
        """
        Test the create guardian API endpoint with a future date of birth.
        """
        guardian_data = self.guardians_data[0]
        guardian_data["user"]["date_of_birth"] = (
            date.today().replace(year=date.today().year + 5).isoformat()
        )
        guardian_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_guardian_with_valid_student(self):
        """
        Test the create guardian API endpoint with a valid student.
        """
        # create one student
        url = reverse("students:student-list")
        student_data = self.students_data[0]
        student_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(url, student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        student_response_data = response.data

        # create a guardian
        guardian_data = self.guardians_data[0]
        guardian_data["user"]["institution"] = self.admin1.institution.id
        guardian_data["wards"].append(student_response_data.get("id"))
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_guardian_with_date_of_birth_after_student(self):
        """
        Test the create guardian API endpoint with a date of birth after the
        student's date of birth.
        """
        # create one student
        url = reverse("students:student-list")
        student_data = self.students_data[0]
        student_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(url, student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        student_response_data = response.data

        # create a guardian
        guardian_data = self.guardians_data[0]
        # add ten years after student's date of birth for the guardian
        student_date_of_birth = date.fromisoformat(
            student_response_data["user"]["date_of_birth"]
        )
        guardian_data["user"]["date_of_birth"] = (
            student_date_of_birth.replace(
                year=student_date_of_birth.year + 10
            )
        ).isoformat()
        guardian_data["user"]["institution"] = self.admin1.institution.id
        guardian_data["wards"].append(student_response_data.get("id"))
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_guardian(self):
        """
        Test the update guardian API endpoint.
        """
        # create one student
        url = reverse("students:student-list")
        student_data = self.students_data[0]
        student_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(url, student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        student_response_data = response.data

        # create a guardian
        guardian_data = self.guardians_data[0]
        guardian_data["user"]["institution"] = self.admin1.institution.id
        guardian_data["wards"].append(student_response_data.get("id"))
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        guardian_response_data = response.data

        # now update the guardian with PUT request to the API
        guardian_data = self.guardians_data[1]
        guardian_data["user"]["institution"] = self.admin1.institution.id
        guardian_data["wards"].append(student_response_data.get("id"))
        response = self.client.put(
            reverse(
                "students:guardian-detail",
                args=[guardian_response_data.get("id")],
            ),
            guardian_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("user").get("username"),
            self.guardians_data[1].get("user").get("username"),
        )

    def test_delete_guardian(self):
        """
        Test the delete guardian API endpoint.
        """
        # create one student
        url = reverse("students:student-list")
        student_data = self.students_data[0]
        student_data["user"]["institution"] = self.admin1.institution.id
        response = self.client.post(url, student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        student_response_data = response.data

        # create a guardian
        guardian_data = self.guardians_data[0]
        guardian_data["user"]["institution"] = self.admin1.institution.id
        guardian_data["wards"].append(student_response_data.get("id"))
        response = self.client.post(
            reverse("students:guardian-list"), guardian_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        guardian_response_data = response.data

        self.assertEqual(User.objects.count(), 4)

        # now delete the guardian
        response = self.client.delete(
            reverse(
                "students:guardian-detail",
                args=[guardian_response_data.get("id")],
            )
        )

        # confirm it was deleted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
