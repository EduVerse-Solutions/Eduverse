from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from core.api import data as utils_data
from core.api import utils
from core.models import Institution, User


class APIRootViewTest(APITestCase):
    """Test cases for the API Root view."""

    def test_api_root_view_without_authentication(self):
        """Tests the API root view without authentication."""
        response = self.client.get(
            reverse("core-api:api-root"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_root_with_authentication(self):
        """Tests the API root view with a super admin user."""
        user = utils.create_super_admin()

        self.assertIsNone(user.institution)
        self.client.force_authenticate(user=user)
        self.assertTrue(user.is_authenticated)

        # get the root page of the API
        response = self.client.get(reverse("core-api:api-root"))

        # only admins should have access to the API
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_root_with_student_user(self):
        """Tests the API root view with a student user."""
        user = utils.create_student()

        self.assertIsNone(user.institution)
        self.client.force_authenticate(user=user)
        self.assertTrue(user.is_authenticated)

        # get the root page of the API
        response = self.client.get(reverse("core-api:api-root"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_root_with_guardian_user(self):
        """Tests the API root view with a guardian user."""
        user = utils.create_guardian()

        self.assertIsNone(user.institution)
        self.client.force_authenticate(user=user)
        self.assertTrue(user.is_authenticated)

        # get the root page of the API
        response = self.client.get(reverse("core-api:api-root"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserViewSetTest(APITestCase):
    """
    Test case for the UserViewSet class.

    This test case contains test methods to verify the functionality of the
    UserViewSet class, which is responsible for handling API requests related
    to user management.
    """

    def setUp(self):
        """
        Set up the test case by creating a super admin user and authenticating the client.
        """
        self.admin1 = utils.create_super_admin(assign_institution=True)
        self.client.force_authenticate(user=self.admin1)

    def test_list_users(self):
        """
        Test the list users API endpoint.
        """
        url = reverse("core-api:user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user(self):
        """
        Test the retrieve user API endpoint.
        """
        url = reverse(
            "core-api:user-detail",
            kwargs={"pk": self.admin1.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        """
        Test the create user API endpoint.
        """
        url = reverse("core-api:user-list")
        user_data = utils_data.user_list[1].copy()
        user_data["institution"] = self.admin1.institution.pk
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_institution_field(self):
        """
        Test the create user API endpoint without an institution field.
        """
        url = reverse("core-api:user-list")
        user_data = utils_data.user_list[1].copy()
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_admin_no_institution(self):
        """
        Test the create user endpoint with an admin who has hasn't created
        an institution yet.
        """
        url = reverse("core-api:user-list")
        institution = self.admin1.institution
        self.admin1.institution = None
        user_data = utils_data.user_list[2].copy()
        user_data["institution"] = institution.pk
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_invalid_institution(self):
        """
        Test the create user API endpoint with an invalid institution.
        """
        url = reverse("core-api:user-list")
        user_data = utils_data.user_list[1].copy()
        user_data["institution"] = 1000
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_invalid_role(self):
        """
        Test the create user API endpoint with an invalid role.
        """
        url = reverse("core-api:user-list")
        user_data = utils_data.user_list[1].copy()
        user_data["institution"] = self.admin1.institution.pk
        self.admin1.role = "Student"
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin1.role = "Super Admin"

    def test_update_user(self):
        """
        Test the update user API endpoint.
        """
        url = reverse("core-api:user-detail", kwargs={"pk": self.admin1.pk})
        data = {"username": "updated_user"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "updated_user")

    def test_update_user_with_a_nonexistent_id(self):
        """
        Test the update user API endpoint with an id that does not exist in
        their institution.
        """
        new_admin_data = utils_data.user_list[0].copy()
        new_admin_data["email"] = "fakea_dmin@email.com"
        new_admin_data["username"] = "fake_admin2"
        new_admin_data["phone_number"] = "+233591236723"

        new_admin = utils.create_super_admin(**new_admin_data)
        url = reverse("core-api:user-detail", kwargs={"pk": new_admin.pk})
        data = {"username": "updated_user"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user(self):
        """
        Test the delete user API endpoint.
        """
        url = reverse("core-api:user-detail", kwargs={"pk": self.admin1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # now let's try retrieving the deleted user
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class InstitutionViewSetTest(APITestCase):
    """
    Test case for the InstitutionViewSet class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = utils.create_super_admin(assign_institution=True)
        self.institution = Institution.objects.first()
        self.institution.name = "Test Institution"
        self.institution.save()
        self.assertEqual(Institution.objects.count(), 1)
        self.assertEqual(self.institution, self.user.institution)

        # use Token Authentication for this test
        self.token = Token.objects.get(user=self.user).key
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_list_institutions(self):
        """
        Test the list institutions API endpoint.
        """
        response = self.client.get(reverse("core-api:institution-list"))
        results = response.data.get("results")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), 1)
        institution = results[0]
        self.assertEqual(institution.get("name"), "Test Institution")
        self.assertEqual(institution.get("owner"), self.institution.owner_id)

    def test_create_institution(self):
        """
        Test the create institution API endpoint.
        """
        institution_data = utils_data.institution_list[1].copy()
        institution_data["name"] = "New Institution"
        institution_data["owner"] = self.user.id
        institution_data["phone_number"] = "+233591236787"
        institution_data["email"] = "new_institution@example.com"
        self.user.institution = None
        self.user.save()

        response = self.client.post(
            reverse("core-api:institution-list"), institution_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Institution.objects.count(), 2)
        self.assertTrue(Institution.objects.filter(name="New Institution"))

    def test_create_institution_with_admin_from_another_institution(self):
        """
        Test creating an institution with an admin from another institution.
        """
        new_admin_data = utils_data.user_list[0].copy()
        new_admin_data["email"] = "fakeadmin@email.com"
        new_admin_data["username"] = "fake_admin"
        new_admin_data["phone_number"] = "233591236787"

        new_admin = utils.create_super_admin(**new_admin_data)

        institution_data = utils_data.institution_list[2].copy()
        institution_data["name"] = "New Institution"
        institution_data["owner"] = self.user.id
        institution_data["phone_number"] = "233591236787"
        institution_data["email"] = "new_institution@example.com"
        institution_data["owner"] = new_admin.id

        while (
            institution_data["phone_number"] == self.institution.phone_number
        ):
            institution_data["phone_number"] = (
                utils_data.generate_phone_number()
            )

        response = self.client.post(
            reverse("core-api:institution-list"), institution_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Institution.objects.count(), 1)

    def test_retrieve_institution(self):
        """
        Test the retrieve institution API endpoint.
        """
        url = reverse(
            "core-api:institution-detail", kwargs={"pk": self.institution.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Institution")

    def test_partial_update_institution(self):
        """
        Test the partial update institution API endpoint.
        """
        url = reverse(
            "core-api:institution-detail", kwargs={"pk": self.institution.id}
        )
        response = self.client.patch(
            url,
            {"name": "Updated Institution"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Institution.objects.get(id=self.institution.id).name,
            "Updated Institution",
        )

    def test_delete_institution(self):
        """
        Test the delete institution API endpoint.
        """
        url = reverse(
            "core-api:institution-detail", kwargs={"pk": self.institution.id}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Institution.objects.count(), 0)

        # now try retrieving the deleted instance, deleting an institution
        # deletes the user as well
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # finally verify the user was deleted
        self.assertEqual(User.objects.count(), 0)
