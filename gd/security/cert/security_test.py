#
#   Copyright 2019 - The Android Open Source Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import time

from bluetooth_packets_python3 import hci_packets
from cert.event_stream import EventStream
from cert.gd_base_test import GdBaseTestClass
from cert.py_security import PySecurity
from facade import common_pb2 as common
from google.protobuf import empty_pb2 as empty_proto
from hci.facade import controller_facade_pb2 as controller_facade
from hci.facade import le_initiator_address_facade_pb2 as le_initiator_address_facade
from l2cap.classic.facade_pb2 import ClassicSecurityPolicy
from neighbor.facade import facade_pb2 as neighbor_facade
from security.cert.cert_security import CertSecurity
from security.facade_pb2 import AuthenticationRequirements
from security.facade_pb2 import BondMsgType
from security.facade_pb2 import IoCapabilities
from security.facade_pb2 import OobDataPresent
from security.facade_pb2 import UiMsgType


class SecurityTest(GdBaseTestClass):
    """
        Collection of tests that each sample results from 
        different (unique) combinations of io capabilities, authentication requirements, and oob data.
    """

    # Possible IO Capabilities
    io_capabilities = (
        IoCapabilities.DISPLAY_ONLY,
        IoCapabilities.DISPLAY_YES_NO_IO_CAP,
        # TODO(optedoblivion): Uncomment when Passkey Entry is implemented in ClassicPairingHandler
        #IoCapabilities.KEYBOARD_ONLY,
        IoCapabilities.NO_INPUT_NO_OUTPUT)

    # Possible Authentication Requirements
    auth_reqs = (
        AuthenticationRequirements.NO_BONDING,
        # TODO(optedoblivion): Figure out MITM cases
        AuthenticationRequirements.NO_BONDING_MITM_PROTECTION,
        AuthenticationRequirements.DEDICATED_BONDING,
        AuthenticationRequirements.DEDICATED_BONDING_MITM_PROTECTION,
        AuthenticationRequirements.GENERAL_BONDING,
        AuthenticationRequirements.GENERAL_BONDING_MITM_PROTECTION)

    # Possible Out-of-Band data options
    oob_present = (
        OobDataPresent.NOT_PRESENT,
        # TODO(optedoblivion): Uncomment when OOB is implemented in root canal
        #"P192_PRESENT",
        #"P256_PRESENT",
        #"P192_AND_256_PRESENT"
    )

    def setup_class(self):
        super().setup_class(dut_module='SECURITY', cert_module='L2CAP')

    def setup_test(self):
        super().setup_test()

        self.dut.neighbor.EnablePageScan(neighbor_facade.EnableMsg(enabled=True))
        self.cert.neighbor.EnablePageScan(neighbor_facade.EnableMsg(enabled=True))

        self.dut.name = b'DUT Device'
        self.dut.address = self.dut.hci_controller.GetMacAddress(empty_proto.Empty()).address
        self.cert.name = b'Cert Device'
        self.cert.address = self.cert.hci_controller.GetMacAddress(empty_proto.Empty()).address

        # TODO(optedoblivion): Make this happen in PySecurity or GdDevice
        self.dut.hci_controller.WriteLocalName(controller_facade.NameMsg(name=self.dut.name))
        self.cert.hci_controller.WriteLocalName(controller_facade.NameMsg(name=self.cert.name))

        self.dut_security = PySecurity(self.dut)
        self.cert_security = CertSecurity(self.cert)

        self.dut_address = common.BluetoothAddressWithType(
            address=common.BluetoothAddress(address=bytes(b'DD:05:04:03:02:01')), type=common.RANDOM_DEVICE_ADDRESS)
        privacy_policy = le_initiator_address_facade.PrivacyPolicy(
            address_policy=le_initiator_address_facade.AddressPolicy.USE_STATIC_ADDRESS,
            address_with_type=self.dut_address)
        self.dut.security.SetLeInitiatorAddressPolicy(privacy_policy)

    def teardown_test(self):
        self.dut_security.close()
        self.cert_security.close()
        super().teardown_test()

    # Initiates the numeric comparison test
    def _run_ssp_numeric_comparison(self, initiator, responder, init_ui_response, resp_ui_response,
                                    expected_init_ui_event, expected_resp_ui_event, expected_init_bond_event,
                                    expected_resp_bond_event):
        initiator.enable_secure_simple_pairing()
        responder.enable_secure_simple_pairing()
        initiator.create_bond(responder.get_address(), common.BluetoothAddressTypeEnum.PUBLIC_DEVICE_ADDRESS)
        self._verify_ssp_numeric_comparison(initiator, responder, init_ui_response, resp_ui_response,
                                            expected_init_ui_event, expected_resp_ui_event, expected_init_bond_event,
                                            expected_resp_bond_event)

    # Verifies the events for the numeric comparion test
    def _verify_ssp_numeric_comparison(self, initiator, responder, init_ui_response, resp_ui_response,
                                       expected_init_ui_event, expected_resp_ui_event, expected_init_bond_event,
                                       expected_resp_bond_event):
        responder.accept_pairing(initiator.get_address(), resp_ui_response)
        initiator.on_user_input(responder.get_address(), init_ui_response, expected_init_ui_event)
        initiator.wait_for_bond_event(expected_init_bond_event)
        responder.wait_for_bond_event(expected_resp_bond_event)

    def test_setup_teardown(self):
        """
            Make sure our setup and teardown is sane
        """
        pass

    # no_input_no_output + no_input_no_output is JustWorks no confirmation
    def test_dut_initiated_no_input_no_output_no_input_no_output_twice_same_acl(self):
        # Arrange
        self.dut_security.set_io_capabilities(IoCapabilities.NO_INPUT_NO_OUTPUT)
        self.dut_security.set_authentication_requirements(AuthenticationRequirements.DEDICATED_BONDING_MITM_PROTECTION)
        self.dut_security.set_oob_data(OobDataPresent.NOT_PRESENT)
        self.cert_security.set_io_capabilities(IoCapabilities.NO_INPUT_NO_OUTPUT)
        self.cert_security.set_authentication_requirements(AuthenticationRequirements.DEDICATED_BONDING_MITM_PROTECTION)
        self.cert_security.set_oob_data(OobDataPresent.NOT_PRESENT)

        # Act and Assert
        self._run_ssp_numeric_comparison(
            initiator=self.dut_security,
            responder=self.cert_security,
            init_ui_response=True,
            resp_ui_response=True,
            expected_init_ui_event=None,
            expected_resp_ui_event=None,
            expected_init_bond_event=BondMsgType.DEVICE_BONDED,
            expected_resp_bond_event=None)

        self.dut_security.enforce_security_policy(self.cert.address,
                                                  common.BluetoothAddressTypeEnum.PUBLIC_DEVICE_ADDRESS,
                                                  ClassicSecurityPolicy.AUTHENTICATED_ENCRYPTED_TRANSPORT)

        self._verify_ssp_numeric_comparison(
            initiator=self.dut_security,
            responder=self.cert_security,
            init_ui_response=True,
            resp_ui_response=True,
            expected_init_ui_event=None,
            expected_resp_ui_event=None,
            expected_init_bond_event=BondMsgType.DEVICE_BONDED,
            expected_resp_bond_event=None)

        self.dut_security.wait_for_enforce_security_event(expected_enforce_security_event=False)

    # no_input_no_output + no_input_no_output is JustWorks no confirmation
    def test_dut_initiated_no_input_no_output_no_input_no_output_twice_with_remove_bond(self):
        # Arrange
        self.dut_security.set_io_capabilities(IoCapabilities.NO_INPUT_NO_OUTPUT)
        self.dut_security.set_authentication_requirements(AuthenticationRequirements.DEDICATED_BONDING_MITM_PROTECTION)
        self.dut_security.set_oob_data(OobDataPresent.NOT_PRESENT)
        self.cert_security.set_io_capabilities(IoCapabilities.NO_INPUT_NO_OUTPUT)
        self.cert_security.set_authentication_requirements(AuthenticationRequirements.DEDICATED_BONDING_MITM_PROTECTION)
        self.cert_security.set_oob_data(OobDataPresent.NOT_PRESENT)

        # Act and Assert
        self._run_ssp_numeric_comparison(
            initiator=self.dut_security,
            responder=self.cert_security,
            init_ui_response=True,
            resp_ui_response=True,
            expected_init_ui_event=None,
            expected_resp_ui_event=None,
            expected_init_bond_event=BondMsgType.DEVICE_BONDED,
            expected_resp_bond_event=None)

        self.dut_security.remove_bond(self.cert.address, common.BluetoothAddressTypeEnum.PUBLIC_DEVICE_ADDRESS)

        # Give time for ACL to disconnect
        time.sleep(1)

        # Act and Assert
        self._run_ssp_numeric_comparison(
            initiator=self.dut_security,
            responder=self.cert_security,
            init_ui_response=True,
            resp_ui_response=True,
            expected_init_ui_event=None,
            expected_resp_ui_event=None,
            expected_init_bond_event=BondMsgType.DEVICE_BONDED,
            expected_resp_bond_event=None)

    def test_successful_dut_initiated_ssp_numeric_comparison(self):
        test_count = len(self.io_capabilities) * len(self.auth_reqs) * len(self.oob_present) * len(
            self.io_capabilities) * len(self.auth_reqs) * len(self.oob_present)
        logging.info("Loading %d test combinations" % test_count)
        i = 0
        for init_io_capability in self.io_capabilities:
            for init_auth_reqs in self.auth_reqs:
                for init_oob_present in self.oob_present:
                    for resp_io_capability in self.io_capabilities:
                        for cert_auth_reqs in self.auth_reqs:
                            for cert_oob_present in self.oob_present:
                                i = i + 1
                                logging.info("")
                                logging.info("===================================================")
                                logging.info("Running test %d of %d" % (i, test_count))
                                logging.info("DUT Test Config: %d ; %d ; %d " % (init_io_capability, init_auth_reqs,
                                                                                 init_oob_present))
                                logging.info("CERT Test Config: %d ; %d ; %d " % (resp_io_capability, cert_auth_reqs,
                                                                                  cert_oob_present))
                                logging.info("===================================================")
                                logging.info("")
                                self.dut_security.set_io_capabilities(init_io_capability)
                                self.dut_security.set_authentication_requirements(init_auth_reqs)
                                self.dut_security.set_oob_data(init_oob_present)
                                self.cert_security.set_io_capabilities(resp_io_capability)
                                self.cert_security.set_authentication_requirements(cert_auth_reqs)
                                self.cert_security.set_oob_data(cert_oob_present)
                                init_ui_response = True
                                resp_ui_response = True
                                expected_init_ui_event = None  # None is auto accept
                                expected_resp_ui_event = None  # None is auto accept
                                expected_init_bond_event = BondMsgType.DEVICE_BONDED
                                expected_resp_bond_event = None
                                if init_io_capability == IoCapabilities.DISPLAY_ONLY:
                                    if resp_io_capability == IoCapabilities.DISPLAY_YES_NO_IO_CAP:
                                        expected_resp_ui_event = UiMsgType.DISPLAY_YES_NO_WITH_VALUE
                                    elif resp_io_capability == IoCapabilities.KEYBOARD_ONLY:
                                        expected_resp_ui_event = UiMsgType.DISPLAY_PASSKEY_ENTRY
                                elif init_io_capability == IoCapabilities.DISPLAY_YES_NO_IO_CAP:
                                    expected_init_ui_event = UiMsgType.DISPLAY_YES_NO_WITH_VALUE
                                    if resp_io_capability == IoCapabilities.DISPLAY_YES_NO_IO_CAP:
                                        expected_resp_ui_event = UiMsgType.DISPLAY_YES_NO_WITH_VALUE
                                    elif resp_io_capability == IoCapabilities.KEYBOARD_ONLY:
                                        expected_init_ui_event = UiMsgType.DISPLAY_PASSKEY
                                        expected_resp_ui_event = UiMsgType.DISPLAY_PASSKEY_ENTRY
                                    elif resp_io_capability == IoCapabilities.NO_INPUT_NO_OUTPUT:
                                        expected_init_ui_event = UiMsgType.DISPLAY_YES_NO  # No value
                                elif init_io_capability == IoCapabilities.KEYBOARD_ONLY:
                                    expected_init_ui_event = UiMsgType.DISPLAY_PASSKEY_ENTRY
                                    if resp_io_capability == IoCapabilities.DISPLAY_ONLY:
                                        expected_resp_ui_event = UiMsgType.DISPLAY_PASSKEY
                                    elif resp_io_capability == IoCapabilities.DISPLAY_YES_NO_IO_CAP:
                                        expected_resp_ui_event = UiMsgType.DISPLAY_PASSKEY_ENTRY
                                    elif resp_io_capability == IoCapabilities.KEYBOARD_ONLY:
                                        expected_resp_ui_event = UiMsgType.DISPLAY_PASSKEY_ENTRY
                                elif init_io_capability == IoCapabilities.NO_INPUT_NO_OUTPUT:
                                    if resp_io_capability == IoCapabilities.DISPLAY_YES_NO_IO_CAP:
                                        expected_resp_ui_event = UiMsgType.DISPLAY_YES_NO  # No value

                                self._run_ssp_numeric_comparison(
                                    initiator=self.dut_security,
                                    responder=self.cert_security,
                                    init_ui_response=init_ui_response,
                                    resp_ui_response=resp_ui_response,
                                    expected_init_ui_event=expected_init_ui_event,
                                    expected_resp_ui_event=expected_resp_ui_event,
                                    expected_init_bond_event=expected_init_bond_event,
                                    expected_resp_bond_event=expected_resp_bond_event)

                                self.dut_security.remove_bond(self.cert_security.get_address(),
                                                              common.BluetoothAddressTypeEnum.PUBLIC_DEVICE_ADDRESS)
                                self.cert_security.remove_bond(self.dut_security.get_address(),
                                                               common.BluetoothAddressTypeEnum.PUBLIC_DEVICE_ADDRESS)

                                time.sleep(.1)
