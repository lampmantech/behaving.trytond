from behaving.trytond import environment as tenv

# We pull in the personae as we'll probably make use of them to deal
# with multi-user, and as a check that we are working with behaving.
from behaving.personas import environment as personaenv


def before_all(context):
    tenv.before_all(context)
    personaenv.before_all(context)
    context.config.log_capture = False


def after_all(context):
    tenv.after_all(context)
    personaenv.after_all(context)


def before_feature(context, feature):
    tenv.before_feature(context, feature)
    personaenv.before_feature(context, feature)


def after_feature(context, feature):
    tenv.after_feature(context, feature)
    personaenv.after_feature(context, feature)


def before_scenario(context, scenario):
    tenv.before_scenario(context, scenario)
    personaenv.before_scenario(context, scenario)


def after_scenario(context, scenario):
    tenv.after_scenario(context, scenario)
    personaenv.after_scenario(context, scenario)
