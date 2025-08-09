#include "oneshot_timer.h"
#include "esphome/core/log.h"

namespace esphome {
namespace oneshot_timer {

static const char *const TAG = "oneshot_timer";

void OneShotTimer::setup() {
  if (this->auto_start_) {
    this->start();
  }
}

void OneShotTimer::loop() {
  if (this->running_) {
    uint32_t now = millis();
    uint32_t delta = now - this->last_visit_;
    this->last_visit_ = now;

    if (this->remaining_time_ <= delta) {
      // Timer has expired
      ESP_LOGD(TAG, "Timer expired");
      this->remaining_time_ = 0;
      this->running_ = false;
      for (auto *trig : this->on_timeout_trigger_) {
        trig->trigger();
      }
    } else {
      this->remaining_time_ -= delta;
    }
  }
}

void OneShotTimer::dump_config() {
  ESP_LOGCONFIG(TAG, "One-Shot Timer:");
  ESP_LOGCONFIG(TAG, "  Interval: %ums", this->interval_);
  ESP_LOGCONFIG(TAG, "  Auto-Start: %s", this->auto_start_ ? "true" : "false");
}

void OneShotTimer::start(optional<uint32_t> interval) {
  ESP_LOGD(TAG, "Timer starting with interval %ums", interval.has_value() ? interval.value() : this->interval_);
  if (interval.has_value()) {
    this->remaining_time_ = interval.value();
  } else {
    this->remaining_time_ = this->interval_;
  }
  this->running_ = true;
  this->last_visit_ = millis();
  for (auto *trig : this->on_start_trigger_) {
    trig->trigger();
  }
}

void OneShotTimer::pause() {
  if (this->running_) {
    this->running_ = false;
    for (auto *trig : this->on_pause_trigger_) {
      trig->trigger();
    }
  }
}

void OneShotTimer::resume() {
  if (!this->running_) {
    if (this->remaining_time_ > 0) {
      ESP_LOGD(TAG, "Resuming timer");
      this->running_ = true;
      this->last_visit_ = millis();
    } else {
      ESP_LOGW(TAG, "Can't resume an expired timer");
    }
  } else {
    ESP_LOGW(TAG, "Can't resume a running timer");
  }
}

}  // namespace oneshot_timer
}  // namespace esphome
