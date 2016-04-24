import time
import datetime

import pytest

import kbb


def test_datetime_conversion_easy():
    k = kbb.Kbb()
    string = '1985-04-12T23:20:50.52Z'
    timeobj = datetime.datetime(1985, 4, 12, hour=23, minute=20, second=50, microsecond=520000)
    assert k._convert_str_to_iso3339(string) == timeobj


def test_datetime_conversion_gtasks_example():
    k = kbb.Kbb()
    string = '2010-10-15T12:00:00.000Z'
    timeobj = datetime.datetime(2010, 10, 15, hour=12, minute=0, second=0, microsecond=0)
    assert k._convert_str_to_iso3339(string) == timeobj


def test_datetime_conversion_gtasks_broken():
    k = kbb.Kbb()
    string = '2010-10-15T12:00:00.000P'

    with pytest.raises(ValueError):
        k._convert_str_to_iso3339(string)


def test_generate_uuid_length():
    k = kbb.Kbb()
    assert len(k._generate_uuid(1)) == 1
    assert len(k._generate_uuid(42)) == 42
    assert len(k._generate_uuid(100)) == 100


def test_locate_task_easy():
    k = kbb.Kbb()
    task = k.new_task('test task', cloud_sync=False)
    assert k._locate_task(task.task_id)
    k.delete_task(task.task_id, cloud_sync=False)


def test_locate_task_error():
    k = kbb.Kbb()
    task = k.new_task('test task error', cloud_sync=False)

    with pytest.raises(Exception):
        k._locate_task(task.task_id[:len(task.task_id) - 1])

    k.delete_task(task.task_id, cloud_sync=False)


def test_get_all_idents_present():
    k = kbb.Kbb()

    task = k.new_task('ident test task', cloud_sync=False)
    assert task.task_id in k._get_all_task_ids_in_db()
    k.delete_task(task.task_id, cloud_sync=False)


def test_get_all_idents_not_present():
    k = kbb.Kbb()

    task = k.new_task('ident test task not present', cloud_sync=False)
    assert task.task_id[:len(task.task_id) - 1] not in k._get_all_task_ids_in_db()
    k.delete_task(task.task_id, cloud_sync=False)
