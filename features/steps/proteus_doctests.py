# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from behave import *
import proteus
import random

@step('proteus/test_model test_class_cache')
def step_impl(context):
    User1 = proteus.Model.get('res.user')
    User2 = proteus.Model.get('res.user')
    assert id(User1) == id(User2)

    proteus.Model.reset()
    User3 = proteus.Model.get('res.user')
    assert id(User1) != id(User3)

@step('proteus/test_model test_class_method')
def step_impl(context):
    User = proteus.Model.get('res.user')
    assert len(User.search([('login', '=', 'admin')], {}))

@step('proteus/test_model test_find')
def step_impl(context):
    User = proteus.Model.get('res.user')
    admin = User.find([('login', '=', 'admin')])[0]
    assert admin.login == 'admin'

@step('proteus/test_model test_many2one')
def step_impl(context):
    User = proteus.Model.get('res.user')
    admin = User.find([('login', '=', 'admin')])[0]
    assert isinstance(admin.create_uid, User)
    try:
        admin.create_uid = 'test'
        raise RuntimeError
    except AssertionError:
        pass
    admin.create_uid = admin
    admin.create_uid = None

    User(write_uid=False)

@step('proteus/test_model test_one2many')
def step_impl(context):
    Group = proteus.Model.get('res.group')
    administration = Group.find([('name', '=', 'Administration')])[0]
    assert isinstance(administration.model_access, list)
    assert isinstance(administration.model_access[0],
        proteus.Model.get('ir.model.access'))
    try:
        administration.model_access = []
        raise RuntimeError
    except AttributeError:
        pass

@step('proteus/test_model test_many2many')
def step_impl(context):
    User = proteus.Model.get('res.user')
    admin = User.find([('login', '=', 'admin')])[0]
    assert isinstance(admin.groups, list)
    assert isinstance(admin.groups[0],
        proteus.Model.get('res.group'))
    try:
        admin.groups = []
        raise RuntimeError
    except AttributeError:
        pass

# TODO test date

@step('proteus/test_model test_reference')
def step_impl(context):
    Attachment = proteus.Model.get('ir.attachment')
    User = proteus.Model.get('res.user')
    admin = User.find([('login', '=', 'admin')])[0]
    attachment = Attachment()
    attachment.name = 'Test %d' % int(random.random()*1000000)
    attachment.resource = admin
    attachment.save()
    assert attachment.resource == admin

@step('proteus/test_model test_id_counter')
def step_impl(context):
    User = proteus.Model.get('res.user')
    test1 = User()
    assert test1.id < 0
    test2 = User()
    assert test2.id < 0
    assert test1.id != test2.id

@step('proteus/test_model test_init')
def step_impl(context):
    User = proteus.Model.get('res.user')
    assert User(1).id == 1
    assert User(name='Foo').name == 'Foo'

    Lang = proteus.Model.get('ir.lang')
    en_US = Lang.find([('code', '=', 'en_US')])[0]
    assert User(language=en_US).language == en_US
    assert User(language=en_US.id).language == en_US

    Group = proteus.Model.get('res.group')
    groups = Group.find()
    assert len(User(groups=groups).groups) == len(groups)
    assert len(User(groups=[x.id for x in groups]).groups) == len(groups)

@step('proteus/test_model test_save')
def step_impl(context):
    User = proteus.Model.get('res.user')
    test = User()
    test.name = 'Test'
    test.login = 'test'
    test.save()
    assert test.id > 0

    test = User(test.id)
    assert test.name == 'Test'
    assert test.login == 'test'
    assert test.active

    test.signature = 'Test signature'
    assert test.signature == 'Test signature'
    test.save()
    assert test.signature == 'Test signature'
    test = User(test.id)
    assert test.signature == 'Test signature'

    Group = proteus.Model.get('res.group')
    test2 = User(name='Test 2', login='test2',
            groups=[Group(name='Test 2')])
    test2.save()
    assert test2.id > 0
    assert test2.name == 'Test 2'
    assert test2.login == 'test2'

@step('proteus/test_model test_save_many2one')
def step_impl(context):
    User = proteus.Model.get('res.user')
    test = User()
    test.name = 'Test save many2one'
    test.login = 'test_save_many2one'
    test.save()

    Lang = proteus.Model.get('ir.lang')
    en_US = Lang.find([('code', '=', 'en_US')])[0]
    test.language = en_US
    test.save()
    assert test.language == en_US

    test.language = None
    test.save()
    assert not test.language

@step('proteus/test_model test_save_one2many')
def step_impl(context):
    """
    FixMe:
    ininite recursion:

> /n/data/TrytonOpenERP/lib/python2.7/site-packages/trytond-3.2.4-py2.7.egg/trytond/model/modelsql.py(1154)<genexpr>()
-> return And((convert(d) for d in (
(Pdb) up
> /n/data/TrytonOpenERP/lib/python2.7/site-packages/trytond-3.2.4-py2.7.egg/trytond/model/modelsql.py(1155)convert()
-> domain[1:] if domain[0] == 'AND' else domain)))
(Pdb) up
> /n/data/TrytonOpenERP/lib/python2.7/site-packages/trytond-3.2.4-py2.7.egg/trytond/model/modelsql.py(1154)<genexpr>()
-> return And((convert(d) for d in (

    """
    return
    Group = proteus.Model.get('res.group')
    group = Group()
    group.name = 'Test save one2many'
    group.save()

    ModelAccess = proteus.Model.get('ir.model.access')
    Model_ = proteus.Model.get('ir.model')
    model_access = ModelAccess()
    model_access.model = proteus.Model_.find([('model', '=', 'res.group')])[0]
    model_access.perm_read = True
    model_access.perm_write = True
    model_access.perm_create = True
    model_access.perm_delete = True

    group.model_access.append(model_access)
    group.save()
    assert len(group.model_access) == 1

    model_access_id = group.model_access[0].id

    group.name = 'Test save one2many bis'
    group.model_access[0].description = 'Test save one2many'
    group.save()
    assert group.model_access[0].description == \
            'Test save one2many'

    group.model_access.pop()
    group.save()
    assert group.model_access == []
    assert len(ModelAccess.find([('id', '=' == model_access_id)])) == 1

    group.model_access.append(ModelAccess(model_access_id))
    group.save()
    assert len(group.model_access) == 1

    group.model_access.remove(group.model_access[0])
    group.save()
    assert group.model_access == []
    assert len(ModelAccess.find([('id', '=' == model_access_id)])) == 0

@step('proteus/test_model test_save_many2many')
def step_impl(context):
    User = proteus.Model.get('res.user')
    test = User()
    test.name = 'Test save many2many'
    test.login = 'test_save_many2many'
    test.save()

    Group = proteus.Model.get('res.group')
    group = Group()
    group.name = 'Test save many2many'
    group.save()

    test.groups.append(group)
    test.save()
    assert len(test.groups) == 1

    group_id = test.groups[0].id

    test.name = 'Test save many2many bis'
    test.groups[0].name = 'Test save many2many bis'
    test.save()
    assert test.groups[0].name == \
            'Test save many2many bis'

    test.groups.pop()
    test.save()
    assert test.groups == []
    assert len(Group.find([('id', '=', group_id)])) == 1

    test.groups.append(Group(group_id))
    test.save()
    assert len(test.groups) == 1

    test.groups.remove(test.groups[0])
    test.save()
    assert test.groups == []
    assert len(Group.find([('id', '=', group_id)])) == 0

@step('proteus/test_model test_cmp')
def step_impl(context):
    User = proteus.Model.get('res.user')
    test = User()
    test.name = 'Test cmp'
    test.login = 'test_cmp'
    test.save()
    admin1 = User.find([('login', '=', 'admin')])[0]
    admin2 = User.find([('login', '=', 'admin')])[0]

    assert admin1 == admin2
    assert admin1 != test
    assert admin1 != None
    assert admin1 != False

#    assertRaises(NotImplementedError, lambda: admin1 == 1)

@step('proteus/test_model test_default_set')
def step_impl(context):
    User = proteus.Model.get('res.user')
    Group = proteus.Model.get('res.group')
    group_ids = [x.id for x in Group.find()]
    test = User()
    test._default_set({
        'name': 'Test',
        'groups': group_ids,
        })
    assert test.name == 'Test'
    assert [x.id for x in test.groups] == group_ids

    test = User()
    test._default_set({
        'name': 'Test',
        'groups': [
            {
                'name': 'Group 1',
            },
            {
                'name': 'Group 2',
            },
            ],
        })
    assert test.name == 'Test'
    assert [x.name for x in test.groups] == ['Group 1', 'Group 2']

@step('proteus/test_model test_delete')
def step_impl(context):
    User = proteus.Model.get('res.user')
    test = User()
    test.name = 'Test delete'
    test.login = 'test delete'
    test.save()
    test.delete()

@step('proteus/test_model test_on_change')
def step_impl(context):
    Trigger = proteus.Model.get('ir.trigger')

    trigger = Trigger()

    trigger.on_time = True
    assert trigger.on_create == False

    trigger.on_create = True
    assert trigger.on_time == False

@step('proteus/test_model test_on_change_with')
def step_impl(context):
    Attachment = proteus.Model.get('ir.attachment')

    attachment = Attachment()

    attachment.description = 'Test'
    assert attachment.summary == 'Test'

@step('proteus/test_model test_on_change_set')
def step_impl(context):
    User = proteus.Model.get('res.user')
    Group = proteus.Model.get('res.group')

    test = User()
    test._on_change_set('name', 'Test')
    assert test.name == 'Test'
    group_ids = [x.id for x in Group.find()]
    test._on_change_set('groups', group_ids)
    assert [x.id for x in test.groups] == group_ids

    test._on_change_set('groups', {'remove': [group_ids[0]]})
    assert [x.id for x in test.groups] == group_ids[1:]

    test._on_change_set('groups', {'add': [(-1, {
                        'name': 'Bar',
                        })]})
    assert [x for x in test.groups if x.name == 'Bar']

    test.groups.extend(Group.find())
    group = test.groups[0]
    test._on_change_set('groups', {'update': [{
        'id': group.id,
        'name': 'Foo',
        }]})
    assert [x for x in test.groups if x.name == 'Foo']
