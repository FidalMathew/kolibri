"""
Tests related specifically to the FacilityDataset model.
"""

from django.db.utils import IntegrityError
from django.test import TestCase

from ..models import FacilityUser, Facility, Classroom, LearnerGroup, DeviceOwner, FacilityDataset

class FacilityDatasetTestCase(TestCase):

    def setUp(self):
        self.facility = Facility.objects.create()
        self.classroom = Classroom.objects.create(parent=self.facility)
        self.learner_group = LearnerGroup.objects.create(parent=self.classroom)
        self.facility_user = FacilityUser.objects.create(username="blah", password="#", facility=self.facility)
        self.device_owner = DeviceOwner.objects.create(username="blooh", password="#")

    def test_datasets_equal(self):
        self.assertTrue(self.facility.dataset is not None)
        self.assertEqual(self.facility.dataset, self.classroom.dataset)
        self.assertEqual(self.classroom.dataset, self.learner_group.dataset)
        self.assertEqual(self.learner_group.dataset, self.facility_user.dataset)

    def test_device_owner_has_no_dataset(self):
        self.assertFalse(hasattr(self.device_owner, "dataset"))

    def test_cannot_create_role_across_datasets(self):
        facility2 = Facility.objects.create()
        with self.assertRaises(IntegrityError):
            facility2.add_admin(self.facility_user)

    def test_cannot_pass_inappropriate_dataset(self):
        facility2 = Facility.objects.create()
        with self.assertRaises(IntegrityError):
            FacilityUser.objects.create(facility=self.facility, dataset=facility2.dataset)

    def test_cannot_change_dataset(self):
        facility2 = Facility.objects.create()
        self.facility_user.dataset = facility2.dataset
        with self.assertRaises(IntegrityError):
            self.facility_user.save()

    def test_cannot_change_facility(self):
        facility2 = Facility.objects.create()
        self.facility_user.facility = facility2
        with self.assertRaises(IntegrityError):
            self.facility_user.save()

    def test_manually_passing_dataset_for_new_facility(self):
        dataset = FacilityDataset.objects.create()
        facility = Facility(name="blah", dataset=dataset)
        facility.full_clean()
        facility.save()
        self.assertEqual(dataset, facility.dataset)
