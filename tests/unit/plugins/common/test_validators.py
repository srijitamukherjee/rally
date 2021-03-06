# Copyright 2017: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import ddt

from rally.common.plugin import plugin
from rally.common import validation
from rally.task import scenario
from tests.unit import test


class JsonSchemaValidatorTestCase(test.TestCase):

    def test_validate(self):
        @plugin.base()
        class DummyPluginBase(plugin.Plugin,
                              validation.ValidatablePluginMixin):
            pass

        @validation.add(name="jsonschema")
        @plugin.configure(name="dummy_plugin")
        class DummyPlugin(DummyPluginBase):
            CONFIG_SCHEMA = {"type": "string"}

        result = DummyPluginBase.validate("dummy_plugin", None, {}, "foo")
        self.assertEqual(0, len(result))

        result = DummyPluginBase.validate("dummy_plugin", None, {}, 10)
        self.assertEqual(1, len(result))
        self.assertFalse(result[0].is_valid)
        self.assertIsNone(result[0].etype)
        self.assertIn("10 is not of type 'string'", result[0].msg)

        DummyPlugin.unregister()


@ddt.ddt
class ArgsValidatorTestCase(test.TestCase):

    @ddt.data(({"args": {"a": 10, "b": 20}}, None),
              ({"args": {"a": 10, "b": 20, "c": 30}}, None),
              ({}, "Argument(s) 'a', 'b' should be specified"),
              ({"args": {"foo": 1}},
               "Argument(s) 'a', 'b' should be specified"),
              ({"args": {"a": 1}}, "Argument(s) 'b' should be specified"),
              ({"args": {"a": 1, "b": 1, "foo": 2}},
               "Unexpected argument(s) found ['foo']."))
    @ddt.unpack
    def test_validate(self, config, err_msg):
        @plugin.base()
        class DummyPluginBase(plugin.Plugin,
                              validation.ValidatablePluginMixin):
            is_classbased = True

        @validation.add(name="args-spec")
        @plugin.configure(name="dummy_plugin")
        class DummyPlugin(DummyPluginBase):
            def run(self, a, b, c="spam"):
                pass

        result = DummyPluginBase.validate("dummy_plugin", None, config, None)
        if err_msg is None:
            self.assertEqual(0, len(result))
        else:
            self.assertEqual(1, len(result))
            self.assertFalse(result[0].is_valid)
            self.assertIn(err_msg, result[0].msg)

        DummyPlugin.unregister()

        class DummyPlugin2(DummyPluginBase):
            @scenario.configure(name="dummy_plugin.func_based")
            def func_based(self, a, b, c="spam"):
                pass

        result = scenario.Scenario.validate(
            "dummy_plugin.func_based", None, config, None)

        if err_msg is None:
            self.assertEqual(0, len(result))
        else:
            self.assertEqual(1, len(result))
            self.assertFalse(result[0].is_valid)
            self.assertIn(err_msg, result[0].msg)

        DummyPlugin2.func_based.unregister()
