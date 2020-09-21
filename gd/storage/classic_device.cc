/*
 * Copyright 2020 The Android Open Source Project
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

#include "storage/classic_device.h"

#include <algorithm>

#include "common/strings.h"

namespace bluetooth {
namespace storage {

ClassicDevice::ClassicDevice(ConfigCache* config, std::string section)
    : config_(config), section_(std::move(section)) {}

Device ClassicDevice::Parent() {
  return Device(config_, section_);
}

std::string ClassicDevice::ToLogString() {
  return section_;
}

hci::Address ClassicDevice::GetAddress() {
  // section name of a classic device is its MAC address
  auto addr = hci::Address::FromString(section_);
  ASSERT(addr.has_value());
  return std::move(addr.value());
}

}  // namespace storage
}  // namespace bluetooth