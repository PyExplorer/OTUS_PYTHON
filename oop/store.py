#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tarantool
import time
import json


def with_reconnect(func):
    attempts = 3
    delay = 1

    def wrapper(*args, **kwargs):
        for attempt in range(attempts):
            try:
                return func(*args, **kwargs)
            except Exception:
                time.sleep(delay * attempt)
                continue
    return wrapper


def try_reconnect(func):
    attempts = 3
    delay = 1

    def wrapper(*args, **kwargs):
        for attempt in range(attempts):
            try:
                return func(*args, **kwargs)
            except Exception:
                time.sleep(delay * attempt)
                args[0].connect()
                continue
    return wrapper


class Store(object):
    def __init__(self):
        self.server = ''
        self.scoring_space = ''
        self.interests_space = ''
        self.connect()

    @property
    def is_alive(self):
        try:
            self.scoring_space.select('0')
            return True
        except:
            return False

    @with_reconnect
    def connect(self):
        self.server = tarantool.connection.Connection(
            host="localhost", port=3301
        )
        self.scoring_space = self.server.space('scoring')
        self.interests_space = self.server.space('interests')

    @try_reconnect
    def cache_get(self, key):
        record = self.scoring_space.select(key)
        if record.data:
            live_till = float(record.data[0][2])
            if time.time() < live_till:
                return record.data[0][1]
            self.scoring_space.delete(key)

    @try_reconnect
    def cache_set(self, key, score, cache_time):
        try:
            live_till = str(time.time() + cache_time)
            self.scoring_space.insert((key, score, live_till))
        except tarantool.error.DatabaseError:
            pass

    @try_reconnect
    def get(self, cid):
        try:
            record = self.interests_space.select(cid)
            if record:
                return json.dumps({cid: record[0][1]})
        except:
            pass

    def set_init_data(self):
        try:
            self._clean_base()
            self.scoring_space.insert((
                'uid:ff04603735f81bd3085e47b0e1f98857',
                 10.0,
                 time.time() + 10
            ))
            self.interests_space.insert(('i:1', ['auto', 'books']))
            self.interests_space.insert(('i:2', ['garden', 'birds']))
            self.interests_space.insert(('i:3', ['forest', 'airplane']))
        except:
            pass

    def _clean_base(self):
        try:
            records = self.scoring_space.select()
            for rec in records:
                self.scoring_space.delete(rec[0])

            records = self.interests_space.select()
            for rec in records:
                self.interests_space.delete(rec[0])
        except:
            pass
