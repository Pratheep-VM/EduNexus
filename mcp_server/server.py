from mcp.server.fastmcp import FastMCP

mcp = FastMCP('EduNexus-Tools')

@mcp.tool()
def get_weather(location: str) -> str:
    """Get the current weather for a specific location."""
    if 'tokyo' in location.lower():
        return f'The weather in {location} is 70F and sunny.'
    elif 'london' in location.lower():
        return f'The weather in {location} is 55F and rainy.'
    else:
        return f'The weather in {location} is 65F and cloudy.'

@mcp.tool()
def calculate_grade(score: int) -> str:
    """Calculate the letter grade based on a numeric score (0-100)."""
    if score >= 90: return 'A'
    elif score >= 80: return 'B'
    elif score >= 70: return 'C'
    elif score >= 60: return 'D'
    else: return 'F'

if __name__ == '__main__':
    mcp.run()
