# aplhid
A tool to switch between Fn keys modes for Apple keyboards

Apple keyboards are something special in both bad and good senses of this word. This script tries to help circumventing one of their major flaws -- the absence of Fn key switch, and enables user to change the mode of Fn keys "on the fly". Basically it is enough to run this tool without any argument and you're done. 2 explicit args are supported though: `func` will switch to regular Fn-keys mode, `media` is the opposite one making media actions available with a one key press. `auto` basically right there in the name. All args will trigger a prompt for initramfs rebuild. For those who don't like the default settings, feel free to modify driver parameters in switch_mode function.

To switch Fn keys mode with a hotkey, prepend `pkexec` before script's path in launch command and do not use any args, which will make it skip the initramfs rebuild prompt.

This script is heavily based on Canonical's `prime-switch` tool which is a good starting point for basic scripts like this one.
Thanks, @canonical!
