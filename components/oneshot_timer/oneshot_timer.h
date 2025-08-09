#pragma once

#include <optional>
#include "esphome/core/component.h"
#include "esphome/core/automation.h"
#include "esphome/core/hal.h"

namespace esphome {
namespace oneshot_timer {

class OnTimeoutTrigger : public Trigger<> {};
class OnStartTrigger : public Trigger<> {};
class OnPauseTrigger : public Trigger<> {};

class OneShotTimer : public Component {
 public:
  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::HARDWARE; }

  void set_interval(uint32_t interval) {
    this->interval_ = interval;
    this->remaining_time_ = interval;
  }
  void set_auto_start(bool auto_start) { this->auto_start_ = auto_start; }

  void start(optional<uint32_t> interval = nullopt);
  void pause();
  void resume();
  void add_on_timeout_trigger(OnTimeoutTrigger *trigger) { this->on_timeout_trigger_.push_back(trigger); }
  void add_on_start_trigger(OnStartTrigger *trigger) { this->on_start_trigger_.push_back(trigger); }
  void add_on_pause_trigger(OnPauseTrigger *trigger) { this->on_pause_trigger_.push_back(trigger); }

  uint32_t remaining_time() const { return this->remaining_time_; }
  bool running() const { return this->running_; }

 protected:
  uint32_t interval_{0};  // in milliseconds
  uint32_t remaining_time_{0};
  uint32_t last_visit_{0};
  bool running_{false};
  std::vector<OnTimeoutTrigger *> on_timeout_trigger_;
  std::vector<OnStartTrigger *> on_start_trigger_;
  std::vector<OnPauseTrigger *> on_pause_trigger_;
  bool auto_start_{false};
};

template<typename... Ts> class StartAction : public Action<Ts...> {
 public:
  explicit StartAction(OneShotTimer *parent) : parent_(parent) {}
  TEMPLATABLE_VALUE(uint32_t, interval)

 public:
  void play(Ts... x) override {
    if (this->interval_.has_value()) {
      this->parent_->start(this->interval_.value(x...));
    } else {
      this->parent_->start();
    }
  }

 protected:
  OneShotTimer *parent_;
};

template<typename... Ts> class PauseAction : public Action<Ts...> {
 public:
  explicit PauseAction(OneShotTimer *parent) : parent_(parent) {}

  void play(Ts... x) override { this->parent_->pause(); }

 protected:
  OneShotTimer *parent_;
};

template<typename... Ts> class ResumeAction : public Action<Ts...> {
 public:
  explicit ResumeAction(OneShotTimer *parent) : parent_(parent) {}

  void play(Ts... x) override { this->parent_->resume(); }

 protected:
  OneShotTimer *parent_;
};

}  // namespace oneshot_timer
}  // namespace esphome
