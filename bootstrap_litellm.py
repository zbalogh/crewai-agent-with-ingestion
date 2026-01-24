import litellm

# HARD disable everything proxy / logging related
litellm.disable_logging = True
litellm.disable_proxy = True
litellm.telemetry = False

# Verbosity & debug
litellm.set_verbose = False
litellm.suppress_debug_info = True
