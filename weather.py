from typing import Any

import python_weather
import asyncio

from python_weather.forecast import Forecast


async def getweather() -> [Any, Any, Forecast]:
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        city = "Lviv"
        weather = await client.get(city)

        return weather


if __name__ == '__main__':
    print(asyncio.run(getweather()))
