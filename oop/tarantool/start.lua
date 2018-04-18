#!/usr/bin/tarantool

box.cfg {
    listen = 3301
}

box.once('scoring_space', function()
	s = box.schema.space.create('scoring')
	s:create_index('primary', {unique = true, parts = {1, 'STR'}})
	i = box.schema.space.create('interests')
	i:create_index('primary', {unique = true, parts = {1, 'STR'}})
	end
)
