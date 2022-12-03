# Advent of Code 2022 GPT Solver

<b>PSA: This was hacked together within a few hours, and hasn't been cleaned up. </b>

Public GPT models at this point will likely not solve more than the first few days. 

What this does: 
- Parse the puzzle html, with some reformatting
- Build a prompt containing the puzzle description for all tasks so far (including their solutions)
- Run the generated code with puzzle data and submit

A key point to make it able to solve part 2 is to provide the solution it wrote for part 1 (which at this point has been verified) in the prompt. 


Special thanks to:
- The OpenAI team
- Eric Wastl for creating https://adventofcode.com/
- wimglenn and contributors of https://github.com/wimglenn/advent-of-code-data
