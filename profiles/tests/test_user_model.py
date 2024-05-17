from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import VerifyUserEmail


class CustomUserTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email='test@squest.app', password='password', first_name='Steve', last_name='Jobs')

    def test_user_fullname(self):
        """test the property full name"""
        self.assertEqual('Steve Jobs', self.user.full_name)

    def test_level_up_profile(self):
        """test level up user when they reached they xp to level up"""
        user = self.user

        # Test level 1
        self.assertEqual(1, user.level)

        # Test level up
        user.level_up()
        self.assertEqual(2, user.level)

    def test_reach_level_20_do_exceed_20(self):
        """test to reach level 20, but not exceed 20"""
        user = self.user

        user.level = 19
        self.assertEqual(19, user.level)
        user.level_up()
        self.assertEqual(20, user.level)
        user.level_up()
        self.assertEqual(20, user.level)

    def test_change_xp_needed_to_lvl_up_upon_lvl_up(self):
        """test it will change the needed xp for level up upon leveling up"""
        user = self.user

        self.assertEqual(100, user.xp_to_lvl_up)

        # Test for every level
        for _ in range(1, 20):
            user.level_up()
            self.assertEqual(int(50 * (user.level ** 1.2)), self.user.xp_to_lvl_up)

    def test_level_up_with_exact_xp_needed(self):
        """test if 100/100 -> level up and xp set to zero"""
        user = self.user

        user.xp = 100
        user.level_up()
        self.assertEqual(0, user.xp)
        self.assertEqual(2, user.level)
        self.assertEqual(int(50 * (user.level ** 1.2)), user.xp_to_lvl_up)

    def test_level_up_transfer_xp_to_next_level(self):
        """test if 150/100 -> level up and transfer xp"""
        user = self.user

        user.xp = 150
        user.level_up()
        self.assertEqual(50, user.xp)
        self.assertEqual(2, user.level)
        self.assertEqual(int(50 * (user.level ** 1.2)), user.xp_to_lvl_up)


class VerifyTokenEmailTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email='test@squest.app', password='password', first_name='Steve', last_name='Jobs')
        self.token = VerifyUserEmail.objects.create(user=self.user)

    def test_random_token_on_user_creating(self):
        """
        * Test: activate_token sets is_active to true upon user creating
        * Test: generates new token
        """
        self.assertNotEqual(self.token.token, "")
        self.assertEqual(self.token.is_active, True)
        self.assertEqual(self.token.user.pk, self.user.pk)

    def test_activate_token_method(self):
        """
        * Test: test activate_test method
        * Test: Sets is_active to true
        * Test: creates new token
        """
        self.token.deactivate_token()
        old_token_instance_token = self.token.token

        self.token.activate_token()

        self.assertEqual(self.token.is_active, True)
        self.assertNotEqual(self.token.token, old_token_instance_token)

    def test_deactive_token_method(self):
        """
        * Test: set is_active to false
        * Test: create 20 length token
        """
        self.token.activate_token()
        self.assertEqual(self.token.is_active, True)
        self.assertEqual(len(self.token.token), 6)

        self.token.deactivate_token()
        self.assertEqual(self.token.is_active, False)
        self.assertEqual(len(self.token.token), 20)
