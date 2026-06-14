# -*- coding: utf-8 -*-
import unittest
from beem import Steem
from beem.nodelist import NodeList


class Testcases(unittest.TestCase):

    def test_get_nodes(self):
        nodelist = NodeList()
        nodes = nodelist.get_nodes(exclude_limited=False, dev=True, testnet=True, testnetdev=True)
        self.assertGreaterEqual(len(nodes), 1)

        https_nodes = nodelist.get_nodes(wss=False)
        self.assertGreaterEqual(len(https_nodes), 1)
        self.assertEqual(https_nodes[0][:5], "https")

    def test_steem_nodes(self):
        nodelist = NodeList()
        steem_nodes = nodelist.get_steem_nodes()

        self.assertIn("https://api.campingclub.cc", steem_nodes)
        self.assertIn("https://rpc.campingclub.cc", steem_nodes)
        self.assertGreaterEqual(len(steem_nodes), 1)

    def test_default_steem_node_connects(self):
        stm = Steem()
        self.assertTrue(stm.is_steem)
        self.assertEqual(stm.rpc.url, "https://api.campingclub.cc")
