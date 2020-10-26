

"""

parallelism:    multiple operations at the same time
mutiprocessing: means to spreading tasks over a cpu

concurrency:    broader term than parallelism
                multiple taks have ability to run in overlapping manner
                conc =!=> parallel

threading:      multiple thread take turns exec. tasks

asyncIO
    single threaded single process desing
    uses cooperative multitasking

couroutines
  - functions whose execution you can pause

event loop:
  - event A happens, then B
  - loop constantly waits for events
  - Basically an event loop watches out for when something occurs, and when something that the event loop cares about happens it then calls any code that cares about what happened.
  - asyncio is the eventloop


async expr
  - defining a method with async def makes it a coroutine
await:
async def g():
    await f()
  - pause here and com back when f() is ready
  - is basically yield from, but only works with awaitable objets
  - plain generators don't work with await

async fct
  - is a coroutine that has return statements or await expressions

awaitable object
  - is either a coroutine or an object that defines __await__() technically

difference yield vs. async fct
  - reason is
    - to make shure don't accidentally mix generator-based coroutines with
      other generators since the use of the others are differen


summary:
  - think of async/await as API for asynchronous programming



"""


#if "__main__" == __main__():
#    print('asdf')


import asyncio

async def count():
    print("One")
    await asyncio.sleep(1)
    print("Two")

async def main():
    await asyncio.gather(count(), count(), count())

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")