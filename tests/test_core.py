import datetime

import pytest

import kbb
from kbb.task import Task as Task


#TODO: make the tests not use the actual user's kbb environment


def test_add_task_easy_offline():
    k = kbb.Kbb()
    
    old_len = len(k.get_task_list())
    task = k.new_task('len test task', cloud_sync=False)
    new_len = len(k.get_task_list())
    k.delete_task(task.task_id, cloud_sync=False)

    assert new_len - old_len == 1


def test_add_task_all_params_offline():
    k = kbb.Kbb()

    old_len = len(k.get_task_list())
    task = k.new_task('test full param task',
                      stage=k.get_stage_names()[0],
                      due=datetime.datetime.today(),
                      notes='note',
                      status=Task.NOTDONE,
                      cloud_sync=False)
    new_len = len(k.get_task_list())
    k.delete_task(task.task_id, cloud_sync=False)

    assert new_len - old_len == 1


def test_delete_easy_offline():
    k = kbb.Kbb()

    old_len = len(k.get_task_list())
    task = k.new_task('del test task', cloud_sync=False)
    new_len = len(k.get_task_list())
    k.delete_task(task.task_id, cloud_sync=False)

    assert new_len - old_len == 1
    assert task.task_id not in k._get_all_task_ids_in_db()


def test_delete_missing_offline():
    k = kbb.Kbb()

    old_len = len(k.get_task_list())
    task = k.new_task('del test task', cloud_sync=False)
    new_len = len(k.get_task_list())
    k.delete_task(task.task_id, cloud_sync=False)

    assert new_len - old_len == 1
    assert task.task_id not in k._get_all_task_ids_in_db()

    k.delete_task(task.task_id, cloud_sync=False)


def test_add_task_online():
    k = kbb.Kbb()

    task_name = 'online add task test'

    old_len = len(k._get_all_cloud_tasks())
    task = k.new_task(task_name)
    new_len = len(k._get_all_cloud_tasks())

    new_task_id = None
    for t in k.get_task_list():
        if t.title == task_name:
            new_task_id = t.task_id

    # delete test
    if new_task_id:
        k.delete_task(new_task_id)
    else:
        assert False

    assert new_len - old_len == 1


def test_move_task_offline():
    k = kbb.Kbb()

    task = k.new_task('move task test', cloud_sync=False)
    old_stage = task.stage
    new_stage = k.get_stage_names()[-1]
    k.move_task(task.task_id, new_stage, cloud_sync=False)

    assert (k._locate_task(task.task_id).stage) == new_stage


def test_move_task_online():
    k = kbb.Kbb()

    task_name = 'online move task test'

    old_len = len(k._get_all_cloud_tasks())
    task = k.new_task(task_name)
    new_len = len(k._get_all_cloud_tasks())

    new_task_id = None
    for t in k.get_task_list():
        if t.title == task_name:
            new_task_id = t.task_id

    if not new_task_id:
        assert False

    # move task now
    k.move_task(new_task_id, k.get_stage_names()[-1])
    assert k._locate_task(new_task_id).stage == k.get_stage_names()[-1]
    assert k._locate_task(new_task_id).status == Task.DONE

    # clean up
    k.delete_task(new_task_id)
    assert new_len - old_len == 1

