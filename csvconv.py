import csv

# Input and output file paths
input_file = 'movierating.txt'
output_file = 'movies.csv'

# Read all lines, skipping headers
with open(input_file, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

# Skip the header rows (Rank, Movie Title, Description)
lines = lines[3:]

# Group every 3 lines into a record
records = []
for i in range(0, len(lines), 3):
    rank = lines[i]
    title = lines[i+1]
    description = lines[i+2]
    records.append([rank, title, description])

# Write to CSV
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Rank', 'Movie Title', 'Description'])  # CSV header
    writer.writerows(records)

print(f"CSV file '{output_file}' created successfully!")
