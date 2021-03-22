# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
import validators
from frappe.model.document import Document
from press.press.doctype.team.test_team import create_test_team
from press.press.doctype.team_deletion_request.team_deletion_request import (
	TeamDeletionRequest,
)
import requests

class TestTeamDeletionRequest(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.team = create_test_team()
		return super().setUpClass()

	@property
	def team_deletion_request(self):
		if not getattr(self, "_tdr", None):
			try:
				self._tdr = frappe.get_last_doc("Team Deletion Request", filters={"team": self.team.name})
			except frappe.DoesNotExistError:
				self._tdr = self.team.delete(workflow=True)
		return self._tdr

	def test_team_doc_deletion_raise(self):
		self.assertRaises(self.team.delete, frappe.ValidationError)

	def test_team_doc_deletion(self):
		self.assertIsInstance(self.team_deletion_request, TeamDeletionRequest)
		self.assertEqual(self.team_deletion_request.status, "Pending Verification")

	def test_url_for_verification(self):
		deletion_url = self.team_deletion_request.generate_url_for_confirmation()
		self.assertTrue(validators.url(deletion_url))

	def test_team_deletion_api(self):
		deletion_url = self.team_deletion_request.generate_url_for_confirmation()
		res = requests.get(deletion_url)
		self.assertTrue(res.ok)
		self.team_deletion_request.reload()
		self.assertEqual(self.team_deletion_request.status, "Deletion Verified")
