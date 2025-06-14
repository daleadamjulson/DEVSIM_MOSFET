# Copyright 2013 DEVSIM LLC
#
# SPDX-License-Identifier: Apache-2.0

import devsim as ds
from python_packages.simple_physics import GetContactBiasName, PrintCurrents, ReturnCurrents


def rampbias(device, contact, end_bias, step_size, min_step, max_iter, rel_error, abs_error, callback):
    """
    Ramps bias with assignable callback function

    Uses devsim.get_parameter to get the bias currently at the contact being ramped.

    Parameters:
    -----------

    device : name of the device
    contact : contact name
    end_bias : bias for last step
    step_size : initial step size
    min_step : minimum step size
    max_iter : maximum number of iterations
    rel_error : required relative error for convergence
    abs_error : required absolute error for convergence
    callback : callback function that should be called on success.
               See printAllCurrents for an example.

    Description:
    ------------

    Uses GetContactBiasName to get the bias being applied at the contact specified.

    On each successfull bias, the callback function is called.

    Exceptions are raised if there is a failure at the last bias step attempted.

    """

    measurements = []

    start_bias = ds.get_parameter(device=device, name=GetContactBiasName(contact))
    if start_bias < end_bias:
        step_sign = 1
    else:
        step_sign = -1
    step_size = abs(step_size)

    last_bias = start_bias
    while abs(last_bias - end_bias) > min_step:
        print(("%s last end %e %e") % (contact, last_bias, end_bias))
        next_bias = last_bias + step_sign * step_size
        if next_bias < end_bias:
            next_step_sign = 1
        else:
            next_step_sign = -1

        if next_step_sign != step_sign:
            next_bias = end_bias
            print("setting to last bias %e" % (end_bias))
            print("setting next bias %e" % (next_bias))
        ds.set_parameter(device=device, name=GetContactBiasName(contact), value=next_bias)
        try:
            ds.solve(type="dc", absolute_error=abs_error, relative_error=rel_error, maximum_iterations=max_iter)
        except ds.error as msg:
            if str(msg).find("Convergence failure") != 0:
                raise
            ds.set_parameter(device=device, name=GetContactBiasName(contact), value=last_bias)
            step_size *= 0.5
            print("setting new step size %e" % (step_size))
            if step_size < min_step:
                raise RuntimeError("Minimum step size too small")
            continue
        print("Succeeded")
        last_bias = next_bias
        if callback == returnAllCurrents:
            current_data = callback(device)  # returns a dictionary
            measurements.append((next_bias, current_data))
        else:
            callback(device)

    if callback == returnAllCurrents:

        return measurements


def printAllCurrents(device):
    """
    Prints all contact currents on device
    """
    for c in ds.get_contact_list(device=device):
        PrintCurrents(device, c)

def returnAllCurrents(device):
    '''
      Returns a dictionary of all contact currents
    '''
    results = {}
    for c in ds.get_contact_list(device=device):
        current = ReturnCurrents(device, c)
        results[c] = current
    return results
