"""These numerical values are returned by CALDP as process exit status.

This file should be shared/coordinated *verbatim* with CALCLOUD to ensure that
CALCLOUD correctly identifies and handles exit status coming from CALDP.

The intent of these codes is to identify specific error cases defined by CALDP.

Any errors not explicitly handled by CALDP are intended to be mapped to
generic values of 0 or 1 to prevent conflicts with these codes.
"""
import re


_MEMORY_ERROR_NAMES = ["SUBPROCESS_MEMORY_ERROR", "CALDP_MEMORY_ERROR", "CONTAINER_MEMORY_ERROR", "OS_MEMORY_ERROR"]


_EXIT_CODES = dict(
    SUCCESS=0,
    GENERIC_ERROR=1,
    CMDLINE_ERROR=2,
    INPUT_TAR_FILE_ERROR=21,
    ASTROQUERY_ERROR=22,
    STAGE1_ERROR=23,
    STAGE2_ERROR=24,
    S3_UPLOAD_ERROR=25,
    S3_DOWNLOAD_ERROR=26,
    BESTREFS_ERROR=27,
    CREATE_PREVIEWS_ERROR=28,
    SUBPROCESS_MEMORY_ERROR=31,  # See caldp-process for this
    CALDP_MEMORY_ERROR=32,
    CONTAINER_MEMORY_ERROR=33,
    OS_MEMORY_ERROR=34,
    SVM_ERROR=40,
    MVM_ERROR=41,
)


_NAME_EXPLANATIONS = dict(
    SUCCESS="Processing completed successfully.",
    GENERIC_ERROR="An error with no specific CALDP handling occurred somewhere.",
    CMDLINE_ERROR="The program command line invocation was incorrect.",
    INPUT_TAR_FILE_ERROR="An error occurred locating or untarring the inputs tarball.",
    ASTROQUERY_ERROR="An error occurred downloading astroqery: inputs",
    STAGE1_ERROR="An error occurred in this instrument's stage1 processing step. e.g. calxxx",
    STAGE2_ERROR="An error occurred in this instrument's stage2 processing step, e.g astrodrizzle",
    SVM_ERROR="An error occurred while running runsinglehap",
    MVM_ERROR="An error occurred while running runmultihap",
    S3_UPLOAD_ERROR="An error occurred uploading the outputs tarball to S3.",
    S3_DOWNLOAD_ERROR="An error occurred downloading inputs from S3.",
    BESTREFS_ERROR="An error occurred computing or downloading CRDS reference files.",
    CREATE_PREVIEWS_ERROR="An error occurrred creating preview files for processed data.",
    # Potentially see caldp-process bash script for this
    SUBPROCESS_MEMORY_ERROR="A Python MemoryError was detected by scanning the process.txt log.",
    CALDP_MEMORY_ERROR="CALDP generated a Python MemoryError during processing or preview creation.",
    # This is never directly returned.  It's intended to be used to trigger a container memory limit
    CONTAINER_MEMORY_ERROR="The Batch/ECS container runtime killed the job due to memory limits.",
    OS_MEMORY_ERROR="Python raised OSError(Cannot allocate memory...),  possibly fork failure.",
)

_CODE_TO_NAME = dict()

# Set up original module global variables / named constants
for (name, code) in _EXIT_CODES.items():
    globals()[name] = code
    _CODE_TO_NAME[code] = name
    _CODE_TO_NAME[str(code)] = name
    assert name in _NAME_EXPLANATIONS

# -----------------------------------------------------------------------------------------------


def explain(exit_code):
    """Return the text explanation for the specified `exit_code`.

    >>> explain(SUCCESS)
    'EXIT - SUCCESS[0]: Processing completed successfully.'

    >>> explain("SUCCESS")
    'EXIT - SUCCESS[0]: Processing completed successfully.'

    >>> explain(GENERIC_ERROR)
    'EXIT - GENERIC_ERROR[1]: An error with no specific CALDP handling occurred somewhere.'

    >>> explain(SUBPROCESS_MEMORY_ERROR)
    'EXIT - SUBPROCESS_MEMORY_ERROR[31]: A Python MemoryError was detected by scanning the process.txt log.'

    >>> explain(999)
    'EXIT - unhandled exit code: 999'
    """
    if exit_code in _CODE_TO_NAME:
        name = _CODE_TO_NAME[exit_code]
        explanation = _NAME_EXPLANATIONS[name]
    elif exit_code in _NAME_EXPLANATIONS:
        name = exit_code
        exit_code = globals()[name]
        explanation = _NAME_EXPLANATIONS[name]
    else:
        return f"EXIT - unhandled exit code: {exit_code}"
    return f"EXIT - {name}[{exit_code}]: {explanation}"


def is_memory_error(exit_code):
    """Return  True IFF `exit_code` indicates some kind of memory error.

    exit_code may be specified as a name string or integer exit code.

    >>> is_memory_error(GENERIC_ERROR)
    False

    >>> is_memory_error(SUBPROCESS_MEMORY_ERROR)
    True

    >>> is_memory_error(CALDP_MEMORY_ERROR)
    True

    >>> is_memory_error(CONTAINER_MEMORY_ERROR)
    True

    >>> is_memory_error("GENERIC_ERROR")
    False

    >>> is_memory_error("SUBPROCESS_MEMORY_ERROR")
    True
    """
    return (exit_code in [globals()[name] for name in _MEMORY_ERROR_NAMES]) or (exit_code in _MEMORY_ERROR_NAMES)


# -----------------------------------------------------------------------------------------------

# This is steadily improving and as-of Python-3.8 the signal.strsignal() function will exist.

# This is copied from CentOS Linux's /usr/include/bits/signum.h:

_LINUX_SIGNALS_TEXT = """
#define SIGHUP          1       /* Hangup (POSIX).  */
#define SIGINT          2       /* Interrupt (ANSI).  */
#define SIGQUIT         3       /* Quit (POSIX).  */
#define SIGILL          4       /* Illegal instruction (ANSI).  */
#define SIGTRAP         5       /* Trace trap (POSIX).  */
#define SIGABRT         6       /* Abort (ANSI).  */
#define SIGIOT          6       /* IOT trap (4.2 BSD).  */
#define SIGBUS          7       /* BUS error (4.2 BSD).  */
#define SIGFPE          8       /* Floating-point exception (ANSI).  */
#define SIGKILL         9       /* Kill, unblockable (POSIX).  */
#define SIGUSR1         10      /* User-defined signal 1 (POSIX).  */
#define SIGSEGV         11      /* Segmentation violation (ANSI).  */
#define SIGUSR2         12      /* User-defined signal 2 (POSIX).  */
#define SIGPIPE         13      /* Broken pipe (POSIX).  */
#define SIGALRM         14      /* Alarm clock (POSIX).  */
#define SIGTERM         15      /* Termination (ANSI).  */
#define SIGSTKFLT       16      /* Stack fault.  */
#define SIGCHLD         17      /* Child status has changed (POSIX).  */
#define SIGCONT         18      /* Continue (POSIX).  */
#define SIGSTOP         19      /* Stop, unblockable (POSIX).  */
#define SIGTSTP         20      /* Keyboard stop (POSIX).  */
#define SIGTTIN         21      /* Background read from tty (POSIX).  */
#define SIGTTOU         22      /* Background write to tty (POSIX).  */
#define SIGURG          23      /* Urgent condition on socket (4.2 BSD).  */
#define SIGXCPU         24      /* CPU limit exceeded (4.2 BSD).  */
#define SIGXFSZ         25      /* File size limit exceeded (4.2 BSD).  */
#define SIGVTALRM       26      /* Virtual alarm clock (4.2 BSD).  */
#define SIGPROF         27      /* Profiling alarm clock (4.2 BSD).  */
#define SIGWINCH        28      /* Window size change (4.3 BSD, Sun).  */
#define SIGIO           29      /* I/O now possible (4.2 BSD).  */
#define SIGPWR          30      /* Power failure restart (System V).  */
#define SIGSYS          31      /* Bad system call.  */
"""

SIGNUM_EXPLANATION = {}

for line in _LINUX_SIGNALS_TEXT.strip().splitlines():
    match = re.match(r"^\S+\s+(\S+)\s+(\S+)\s+(.*)$", line)
    sigid = match.group(1)
    signum = int(match.group(2))
    sigtext = match.group(3)[2:-2].strip()
    SIGNUM_EXPLANATION[signum] = f"Killed by UNIX signal {sigid}[{signum}]: '{sigtext}'"


def explain_signal(signum):
    """Return a string explaining and representing the Linux signal number `signum`
    which identifies a low level reason why some subprocess died.

    Note that this function can only be used to format negative suprocess
    returncode values which represent signal numbers.  Not all processes are
    killed by signals so this function cannot explain everything, e.g. Python
    failures such as MemoryError don't result in signals.

    >>> explain_signal(8)
    "EXIT - Killed by UNIX signal SIGFPE[8]: 'Floating-point exception (ANSI).'"

    >>> explain_signal(11)
    "EXIT - Killed by UNIX signal SIGSEGV[11]: 'Segmentation violation (ANSI).'"
    """
    return "EXIT - " + SIGNUM_EXPLANATION[signum]


# -----------------------------------------------------------------------------------------------


def test():  # pragma: no cover
    from doctest import testmod
    from . import exit_codes

    return testmod(exit_codes)


if __name__ == "__main__":  # pragma: no cover
    print(test())
