import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.const import (
    CONF_ID,
    CONF_INTERVAL,
    CONF_TRIGGER_ID,
    # CONF_AUTO_START,
    CONF_ON_TIMEOUT,
    #CONF_ON_START,
    #CONF_ON_PAUSE,
)

CODEOWNERS = ["@avishorp"]


oneshot_timer_ns = cg.esphome_ns.namespace("oneshot_timer")
OneShotTimer = oneshot_timer_ns.class_("OneShotTimer", cg.Component)
OnTimeoutTrigger = oneshot_timer_ns.class_("OnTimeoutTrigger")
OnStartTrigger = oneshot_timer_ns.class_("OnStartTrigger")
OnPauseTrigger = oneshot_timer_ns.class_("OnPauseTrigger")
CONF_ON_START = "on_start"
CONF_ON_STOP = "on_stop"
CONF_AUTO_START = "auto_start"
CONF_ON_PAUSE = "on_pause"

# Actions
StartAction = oneshot_timer_ns.class_("StartAction", automation.Action)
PauseAction = oneshot_timer_ns.class_("PauseAction", automation.Action)
ResumeAction = oneshot_timer_ns.class_("ResumeAction", automation.Action)

ONESHOT_TIMER_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(OneShotTimer),
        cv.Required(CONF_INTERVAL): cv.positive_time_period_milliseconds,
        #cv.Optional(CONF_AUTO_START, default=False): cv.boolean,
        cv.Required(CONF_ON_TIMEOUT): automation.validate_automation(
            {
                cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(OnTimeoutTrigger),
            }
        ),
        cv.Optional(CONF_ON_START): automation.validate_automation(
            {cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(OnStartTrigger)}
        ),
        cv.Optional(CONF_ON_PAUSE): automation.validate_automation(
            {cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(OnPauseTrigger)}
        ),
    }
).extend(cv.COMPONENT_SCHEMA)

CONFIG_SCHEMA = cv.All(cv.ensure_list(ONESHOT_TIMER_SCHEMA))


async def to_code(config):
    for timer_config in config:
        var = cg.new_Pvariable(timer_config[CONF_ID])
        await cg.register_component(var, timer_config)

        cg.add(var.set_interval(timer_config[CONF_INTERVAL]))
        cg.add(var.set_auto_start(timer_config[CONF_AUTO_START]))

        for conf in timer_config.get(CONF_ON_TIMEOUT, []):
            trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID])
            await automation.build_automation(trigger, [], conf)
            cg.add(var.add_on_timeout_trigger(trigger))

        for conf in timer_config.get(CONF_ON_START, []):
            trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID])
            await automation.build_automation(trigger, [], conf)
            cg.add(var.add_on_start_trigger(trigger))

        for conf in timer_config.get(CONF_ON_PAUSE, []):
            trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID])
            await automation.build_automation(trigger, [], conf)
            cg.add(var.add_on_pause_trigger(trigger))


@automation.register_action(
    "oneshot_timer.start",
    StartAction,
    automation.maybe_simple_id(
        {
            cv.Required(CONF_ID): cv.use_id(OneShotTimer),
            cv.Optional(CONF_INTERVAL): cv.templatable(
                cv.positive_time_period_milliseconds
            ),
        }
    ),
)
async def oneshot_timer_start_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)
    if CONF_INTERVAL in config:
        template_ = await cg.templatable(config[CONF_INTERVAL], args, cv.uint32_t)
        cg.add(var.set_interval(template_))

        cg.add(var.set_interval(config[CONF_INTERVAL]))
    return var


@automation.register_action(
    "oneshot_timer.pause",
    PauseAction,
    automation.maybe_simple_id(
        {
            cv.Required(CONF_ID): cv.use_id(OneShotTimer),
        }
    ),
)
async def oneshot_timer_pause_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    return cg.new_Pvariable(action_id, template_arg, paren)


@automation.register_action(
    "oneshot_timer.resume",
    ResumeAction,
    automation.maybe_simple_id(
        {
            cv.Required(CONF_ID): cv.use_id(OneShotTimer),
        }
    ),
)
async def oneshot_timer_resume_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    return cg.new_Pvariable(action_id, template_arg, paren)
