lircpy
======

A simple, pure-python script for easily accessing lirc with no external dependencies.

Usage is really simple.  Simply import the module, define a handler and start
the listener.

Example:

    import lircpy

    class Handler(lircpy.Handler):
        # Throttle continous key presses of the same key.  If the user hold down
        # a key on the remote, then we will only respond to every fifth event.  To
        # disable throttling, set this to ``0``.
        THROTTLE = 5

        # The name of my remote as define in my lircd.conf.  To respond to any remote
        # set to ``None``
        REMOTE = "onkyo_rc-707m"   

        # Respond to the "KEY_UP" command as defined in my lircd.conf.
        def KEY_UP(self, data):
            # Handle the KEY_UP command
            print "KEY_UP"

        # Default handler for keys that don't have explicit handlers define.  Note that
        # the default handler is not throttled regardless of what ``THROTTLE`` has been
        # defined as.
        def DEFAULT(self, data):
            print data['key']

    # Start listening for remote commands
    l = lircpy.Lirc(handler=Handler())