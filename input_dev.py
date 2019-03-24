# -*- coding: utf-8-*-
"""This module contains classes and functions for input devices handling."""

import pygame, sys

def find_all(L, x):
    """Find indexes of all occurrences of *x* in list *L*, and return a list of them."""
    out = []
    prev = -1
    while 1:
        try: 
            prev = L.index(x,prev+1)
            out.append(prev)
        except:
            return out

def is_part_of(L1, L2):
    """Return True if *L2* contains all elements of *L1*, False otherwise."""
    for i in L1:
        if i not in L2:
            return False
    return True
    
def setup_joy(jid):
    """Setup joystick with the id *jid*. Returns instance of :py:class:`PadState` associated with that joystick."""
    joy = pygame.joystick.Joystick(jid)
    print "Joystick %d name: %s" % (jid, joy.get_name())
    joy.init()
    ax = joy.get_numaxes()
    bt = joy.get_numbuttons()
    ht = joy.get_numhats()
    print "Number of axes: %d\nNumber of buttons: %d" % (ax, bt)
    print "Number of hats: %d" % ht
    return PadState(bt, ax, ht)

class KeyBindings:
    """This class holds information about key bindings, and allows to bind function ids to input states."""
    def __init__(self, input_state, max_func=0, init_bindings=None):
        """*input_state* - :py:class:`InputState` - input state to use

            *max_func* - int - maximum functions which will be bound to states
            
            *init_bindings* - list of initial bindings, one for each function (starting from 0). Each binding is a list of tuples (device_id, state_id). Keyboard has id 0, and state_ids for it are keys ids as returned by pygame. Joypad 0 has id 1, joypad 1 has id 2 etc. See :py:data:`settings.default_bindings` for an example.
            
            If *init_bindings* is set, *max_func* is ignored. If *init_bindings* is not set, and *max_func* is set, it's used to create empty initial bindings for that many functions. If both are not set, an exception is raised."""
        self.input_state = input_state
        if init_bindings: 
            self.bindings = init_bindings
            max_func = len(init_bindings)
        else: 
            if max_func < 1:
                raise Exception("Can't construct KeyBindings without a valid (>0) max_func number or init_bindings.")
            self.bindings = [[] for i in xrange(max_func)] 
    def bind(self, f):
        """Bind function id *f* to the current input devices state."""
        self.bindings[f] = []
        for i in find_all(self.input_state.kbd_state, True):
            self.bindings[f].append((0, i))    
        for i in xrange(len(self.input_state.joys_state)):
            for j in find_all(self.input_state.joys_state[i].digi_state, True):
                self.bindings[f].append((i+1, j))
    def wait_and_bind(self, f, timer_evt_id=0, dt=10, timeout=100, loop_callback=None, quit_callback=sys.exit, neutral_key=pygame.K_ESCAPE):
        """Wait for state change and then bind function id *f* to the current input devices state.
        
        Optional arguments: *timer_evt_id* - int - what timer id (incremented by *pygame.USEREVENT*) to use; *dt* - int - how long (in msec) to wait between loop cycles (controls the rate at which *loop_callback* is executed); *timeout* - int - how long (in msec) to wait after the first input state change to bind (so quick sequence of key presses will be registered as simultaneous key press); *loop_callback* - function taking no mandatory arguments - optional callback to be executed each loop cycle (e.g. for redrawing of interface); *quit_callback* - function taking no mandatory arguments - callback to execute when *pygame.QUIT* was caught; *neutral_key* - int - id of key which cancels the binding (so it can not be bound to anything), **Escape** by default.  
        """
        self.input_state.reset()
        waiting = True
        tid = pygame.USEREVENT+timer_evt_id
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: quit_callback()  
                if ev.type == pygame.KEYDOWN and ev.key == neutral_key:     
                    self.input_state.reset()
                    return False
                waiting = not self.input_state.process_event_sticky(ev)
            if loop_callback: loop_callback()
            pygame.time.wait(dt)
        waiting = True
        pygame.time.set_timer(tid, timeout)
        while waiting:
            for ev in pygame.event.get():
                if ev.type == tid:
                    waiting = False
                if ev.type == pygame.QUIT: quit_callback()  
                if ev.type == pygame.KEYDOWN and ev.key == neutral_key: 
                    self.input_state.reset()
                    return False
                self.input_state.process_event_sticky(ev)
                if loop_callback: loop_callback()
                pygame.time.wait(dt)
        pygame.time.set_timer(tid, 0)
        self.bind(f)
        self.input_state.reset()
        return True
    def is_dev_state(self, dev_num_tpl):
        """Returns True if device id *dev_num_tpl[0]* has state id *dev_num_tpl[1]*, False otherwise."""
        if dev_num_tpl[0]:
            try:
                out = self.input_state.joys_state[dev_num_tpl[0]-1].digi_state[dev_num_tpl[1]]
            except:
                out = False
            return out
        else:
            return self.input_state.kbd_state[dev_num_tpl[1]]
    def is_triggered(self, f):
        """Return true if function *f* is triggered by the current state."""
        if not self.bindings[f]: 
            return False
        for i in self.bindings[f]:
            if not self.is_dev_state(i):
                return False
        return True
    def get_triggered(self):
        """Returns list of function ids triggered by the current state. If multiple functions are triggered by the same key combination (e.g. one is bound to **left**, another to **shift+left**), only the ones with the biggest combination sizes are returned (so in this case if **shift+left** is pressed, only the second function is returned)."""
        out = find_all(map(self.is_triggered, xrange(len(self.bindings))), True) # find all triggered functions
        out.sort(lambda x, y: cmp(len(self.bindings[y]), len(self.bindings[x]))) # sort them by combo size
        # filter out shorter combos 
        tmp = []
        for i in xrange(len(out)):
            if is_part_of(self.bindings[out[i]], tmp):
                out = out[:i] + out[i+1:]
            else:
                for j in self.bindings[out[i]]:
                    tmp.append(j)
        return out
    def f_to_str(self, f):
        """Return a string representation of input states combo for function id *f*."""
        out = ""
        for i in self.bindings[f]:
            jid = i[0]-1
            if i[0]:
                try:
                    out+=("Joy%d [%s] + " % (jid, self.input_state.joys_state[jid].digi_state_index_to_str(i[1])))
                except:
                    pass
            else:
                out+=("Kbd [%s] + " % pygame.key.name(i[1]))
        if out:
            return out[:-3]
        return "-"
    def __repr__(self):
        """Return representation of this object."""
        return "input_dev.KeyBindings(input_dev.InputState(), init_bindings="+repr(self.bindings)+")"

class PadState:
    """This class holds the state for a joystick/gamepad."""
    def __init__(self, btns, axes, hats, digi_ax_thr=0.9):
        """*btns* - int - number of buttons; *axes* - int - number of axes; *hats* - int - number of hats; *digi_ax_thr* - float (0-1) threshold for treating analog axis position as digital 1"""
        self.btns = btns
        self.axes = axes
        self.hats = hats
        self.digi_ax_thr = digi_ax_thr
        self.reset()
    def reset(self):
        """Reset the state (nothing pressed, everything in neutral position)."""
        self.digi_state = [False for i in xrange(self.btns + self.axes*2 + self.hats*4)] # b a h
    def update_btn(self, btn, state):
        """Update button *btn* (int) state to *state* (bool)."""
        self.digi_state[btn] = state
    def update_digi_axis(self, digi_ax, state):
        """Update axis *digi_ax* (int) state to *state* (bool)."""
        self.digi_state[self.btns+digi_ax] = state
    def update_digi_axis_sticky(self, digi_ax, state):
        """Update axis *digi_ax* (int) state to *state* (bool), but don't change from True to False."""
        self.digi_state[self.btns+digi_ax] |= state
    def update_digi_hat(self, digi_hat, state):
        """Update hat *digi_hat* (int) state to *state* (bool)."""
        self.digi_state[self.btns+self.axes*2+digi_hat] = state   
    def update_digi_hat_sticky(self, digi_hat, state):
        """Update hat *digi_hat* (int) state to *state* (bool), but don't change from True to False."""
        self.digi_state[self.btns+self.axes*2+digi_hat] |= state  
    def update_digi_axis_from_analog(self, ax_num, val):
        """Update axis state from analog axis's number *ax_num* (int) value *val* (float)."""
        self.update_digi_axis(ax_num*2, val>self.digi_ax_thr)
        self.update_digi_axis(ax_num*2+1, (-val)>self.digi_ax_thr)
    def update_digi_axis_from_analog_sticky(self, ax_num, val):
        """Update axis state from analog axis's number *ax_num* (int) value *val* (float), but don't change from True to False."""
        self.update_digi_axis_sticky(ax_num*2, val>self.digi_ax_thr)
        self.update_digi_axis_sticky(ax_num*2+1, (-val)>self.digi_ax_thr)
    def update_digi_hat_from_analog(self, hat_num, val):
        """Update hat state from analog hat's number *hat_num* (int) value *val* (float)."""
        self.update_digi_hat(hat_num*4, val[0]>self.digi_ax_thr)
        self.update_digi_hat(hat_num*4+1, (-val[0])>self.digi_ax_thr)
        self.update_digi_hat(hat_num*4+2, val[1]>self.digi_ax_thr)
        self.update_digi_hat(hat_num*4+3, (-val[1])>self.digi_ax_thr)
    def update_digi_hat_from_analog_sticky(self, hat_num, val):
        """Update hat state from analog hat's number *hat_num* (int) value *val* (float), but don't change from True to False."""
        self.update_digi_hat_sticky(hat_num*4, val[0]>self.digi_ax_thr)
        self.update_digi_hat_sticky(hat_num*4+1, (-val[0])>self.digi_ax_thr)
        self.update_digi_hat_sticky(hat_num*4+2, val[1]>self.digi_ax_thr)
        self.update_digi_hat_sticky(hat_num*4+3, (-val[1])>self.digi_ax_thr)
    def digi_state_index_to_str(self, n):
        """Return a name (string) of the *n*-th element in state."""
        if n < self.btns:
            return "Btn %d" % n
        n -= self.btns
        if n < self.axes*2:
            return "Axis %d%s" % (n/2, ("+", "-")[n%2])
        n -= self.axes*2
        return "Hat %d %s" % (n/4, ("Right", "Left", "Up", "Down")[n%4])

class InputState:
    """This class holds state for input devices (keyboards end joysticks)."""
    def __init__(self, kbd_keys=512):
        """*kbd_keys* - optional int argument, the maximum number of keyboard keys."""
        self.kbd_state = [False for i in xrange(kbd_keys)]
        self.joys_state = []
    def reset(self):
        """Reset the current state to the initial one (nothing pressed)."""
        self.kbd_state = [False for i in self.kbd_state]
        if self.joys_state:
            for i in self.joys_state: i.reset()
    def __str__(self):
        """Convert to human readable string."""
        out = "*** Input State ***\n"
        out += "Keys on keyboard pressed:"
        for i in xrange(len(self.kbd_state)):
            if self.kbd_state[i]: out += " [" + pygame.key.name(i) + "]" 
        for i in xrange(len(self.joys_state)):
            out += ("\nPad %d digital state: " % i) + "".join(map(lambda x: str(int(x)), self.joys_state[i].digi_state))
        out += "\n*******************\n"
        return out
    def get_composite_state():
        """Return the representation of current input devices state as a list of 0/1s."""
        state = [] + self.kbd_state
        for i in self.joys_state:
            state += i.digi_state
        return state
    def process_event_sticky(self, ev):
        """Process event *ev* (instance of **pygame.event.Event**), but ignore key/button release events."""
        if ev.type == pygame.KEYDOWN:
            self.kbd_state[ev.key] = True
            return True
        elif ev.type == pygame.JOYAXISMOTION:
            # DragonRise joypad workaround
            if not (ev.axis == 2 and pygame.joystick.Joystick(ev.joy).get_name() == "DragonRise Inc.   Generic   USB  Joystick  "): 
                self.joys_state[ev.joy].update_digi_axis_from_analog_sticky(ev.axis, ev.value)
                return True
        elif ev.type == pygame.JOYHATMOTION:
            self.joys_state[ev.joy].update_digi_hat_from_analog_sticky(ev.hat, ev.value)
            return True
        elif ev.type == pygame.JOYBUTTONDOWN:
            self.joys_state[ev.joy].update_btn(ev.button, True)
            return True
        else:
            return False
    def process_event(self, ev):
        """Process event *ev* (instance of **pygame.event.Event**)"""
        if ev.type == pygame.KEYDOWN:
            self.kbd_state[ev.key] = True
            return True
        elif ev.type == pygame.KEYUP:
            self.kbd_state[ev.key] = False
            return True
        elif ev.type == pygame.JOYAXISMOTION:
            # DragonRise joypad workaround
            if not (ev.axis == 2 and pygame.joystick.Joystick(ev.joy).get_name() == "DragonRise Inc.   Generic   USB  Joystick  "): 
                self.joys_state[ev.joy].update_digi_axis_from_analog(ev.axis, ev.value)
                return True
            #else:
            #    print "Ignoring axis 2 movement event because it's from a DragonRise gamepad."
        elif ev.type == pygame.JOYHATMOTION:
            self.joys_state[ev.joy].update_digi_hat_from_analog(ev.hat, ev.value)
            return True
        elif ev.type == pygame.JOYBUTTONDOWN:
            self.joys_state[ev.joy].update_btn(ev.button, True)
            return True
        elif ev.type == pygame.JOYBUTTONUP:
            self.joys_state[ev.joy].update_btn(ev.button, False)
            return True
        else:
            return False
    def setup_joys(self):
        """Setup all joysitcks."""
        n = pygame.joystick.get_count()
        if n:
            print "Found %d joysticks" % n
            for jid in xrange(n):
                self.joys_state.append(setup_joy(jid))
        else:
            print "No joysticks found"
            self.joys_state = []
    def uninit_joys(self):
        """Deinitialize all joysticks."""
        self.joys_state = []
        for i in xrange(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.quit()
