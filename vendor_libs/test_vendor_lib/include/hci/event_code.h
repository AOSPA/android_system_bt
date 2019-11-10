/*
 * Copyright 2018 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#pragma once
#include <cstdint>

namespace test_vendor_lib {
namespace hci {

enum class EventCode : uint8_t {
  INQUIRY_COMPLETE = 0x01,
  INQUIRY_RESULT = 0x02,
  CONNECTION_COMPLETE = 0x03,
  CONNECTION_REQUEST = 0x04,
  DISCONNECTION_COMPLETE = 0x05,
  AUTHENTICATION_COMPLETE = 0x06,
  REMOTE_NAME_REQUEST_COMPLETE = 0x07,
  ENCRYPTION_CHANGE = 0x08,
  CHANGE_CONNECTION_LINK_KEY_COMPLETE = 0x09,
  MASTER_LINK_KEY_COMPLETE = 0x0A,
  READ_REMOTE_SUPPORTED_FEATURES_COMPLETE = 0x0B,
  READ_REMOTE_VERSION_INFORMATION_COMPLETE = 0x0C,
  QOS_SETUP_COMPLETE = 0x0D,
  COMMAND_COMPLETE = 0x0E,
  COMMAND_STATUS = 0x0F,
  HARDWARE_ERROR = 0x10,
  FLUSH_OCCURED = 0x11,
  ROLE_CHANGE = 0x12,
  NUMBER_OF_COMPLETED_PACKETS = 0x13,
  MODE_CHANGE = 0x14,
  RETURN_LINK_KEYS = 0x15,
  PIN_CODE_REQUEST = 0x16,
  LINK_KEY_REQUEST = 0x17,
  LINK_KEY_NOTIFICATION = 0x18,
  LOOPBACK_COMMAND = 0x19,
  DATA_BUFFER_OVERFLOW = 0x1A,
  MAX_SLOTS_CHANGE = 0x1B,
  READ_CLOCK_OFFSET_COMPLETE = 0x1C,
  CONNECTION_PACKET_TYPE_CHANGED = 0x1D,
  QOS_VIOLATION = 0x1E,
  PAGE_SCAN_REPETITION_MODE_CHANGE = 0x20,
  FLOW_SPECIFICATION_COMPLETE = 0x21,
  INQUIRY_RESULT_WITH_RSSI = 0x22,
  READ_REMOTE_EXTENDED_FEATURES_COMPLETE = 0x23,
  SYNCHRONOUS_CONNECTION_COMPLETE = 0x2C,
  SYNCHRONOUS_CONNECTION_CHANGED = 0x2D,
  SNIFF_SUBRATING = 0x2E,
  EXTENDED_INQUIRY_RESULT = 0x2F,
  ENCRYPTION_KEY_REFRESH_COMPLETE = 0x30,
  IO_CAPABILITY_REQUEST = 0x31,
  IO_CAPABILITY_RESPONSE = 0x32,
  USER_CONFIRMATION_REQUEST = 0x33,
  USER_PASSKEY_REQUEST = 0x34,
  REMOTE_OOB_DATA_REQUEST = 0x35,
  SIMPLE_PAIRING_COMPLETE = 0x36,
  LINK_SUPERVISION_TIMEOUT_CHANGED = 0x38,
  ENHANCED_FLUSH_COMPLETE = 0x39,
  USER_PASSKEY_NOTIFICATION = 0x3B,
  KEYPRESS_NOTIFICATION = 0x3C,
  REMOTE_HOST_SUPPORTED_FEATURES_NOTIFICATION = 0x3D,
  LE_META_EVENT = 0x3e,
  PHYSICAL_LINK_COMPLETE = 0x40,
  CHANNEL_SELECTED = 0x41,
  DISCONNECTION_PHYSICAL_LINK_COMPLETE = 0x42,
  PHYSICAL_LINK_LOSS_EARLY_WARNING = 0x43,
  PHYSICAL_LINK_RECOVERY = 0x44,
  LOGICAL_LINK_COMPLETE = 0x45,
  DISCONNECTION_LOGICAL_LINK_COMPLETE = 0x46,
  FLOW_SPEC_MODIFY_COMPLETE = 0x47,
  NUMBER_OF_COMPLETED_DATA_BLOCKS = 0x48,
  SHORT_RANGE_MODE_CHANGE_COMPLETE = 0x4C,
};
}
}  // namespace test_vendor_lib
