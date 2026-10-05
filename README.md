# Week 6: Building Testable Design Programs

Read [Reading V10](docs/week_06_reading.pdf), including its final Assignment.
Use [this template](https://github.com/SSUMechE/applied-programming-2026-week06-starter/generate) to create your own private Week 6 repository. The final Assignment is in the Reading.
Use [commands.txt](docs/commands.txt) to copy commands one group at a time.

## 1. Purpose and file to edit

Generate routes around two staggered obstacles using two independent bend
heights. Shorten each route by removing unnecessary bends safely. Select the
shortest route that meets both the clearance and length requirements.

Edit only **src/ap_week06/selection.py** and complete its three marked bodies:

1. generate_route_grid
2. shorten_route
3. select_shortest

Keep the names, signatures, imports and supplied code intact.
evaluate_candidates is complete and supplied. Construction, validation,
geometry, final-path checking, tests, saved output, replay and drawing are also
supplied. tests/test_student.py contains three complete basic examples.
Run these tests as provided. You do not need to write tests or change their file.
The Reading's Assignment gives the full algorithm requirements.

## 2. Prepare repository and environment

Use **Use this template** to create your private
applied-programming-w06-YOUR-STUDENT-ID repository. Open **Anaconda Prompt**.
Replace the folder, account and ID, then run:

```bat
cd /d "C:\your-course-folder"
git clone https://github.com/YOUR-GITHUB-ID/applied-programming-w06-YOUR-STUDENT-ID.git
cd applied-programming-w06-YOUR-STUDENT-ID
git remote -v
```

Both origin addresses must identify your own repository. From its root:

```bat
set PYTHONUTF8=1
conda --no-plugins env create --solver classic --file environment.yml
conda activate applied-programming-w06
python -m pip install -r requirements.txt
python -m pip install -e . --no-build-isolation
python scripts/verify_environment.py
```

Expect ENVIRONMENT PASS. Create the environment once. On another Prompt,
return to the repository, set PYTHONUTF8=1 and activate the existing environment.
Earlier environments and pinned dependencies are unchanged. This geometric
example needs no simulator or GPU.

## 3. Inspect the supplied examples

These two commands work before completing the TODOs:

```bat
python examples/inspect_clearance.py
python examples/inspect_routes.py
```

inspect_clearance.py compares point sampling with the nearest point on the
whole segment using the familiar Week 5 triangle. Sampling adds check points
to the same route. The Week 6 shortening algorithm changes the route.

inspect_routes.py gives a fixed six-point route and its four-point result.
The raw length is about 7.532381 m and exceeds the 6.8 m limit. The final length
is about 6.508503 m and its clearance is 0.257493 m, meeting the 0.25 m limit.
An outer-bend shortcut is permitted. Removing a required inner bend crosses
an obstacle and is rejected. The script supplies these coordinates for
inspection. You implement the general shortening algorithm in the Assignment.

## 4. Complete the three algorithms and run the checks

generate_route_grid(height_min_m,height_max_m,count,settings) uses the supplied
validate_route_grid_parameters function. Use endpoint-inclusive np.linspace.
Combine every a with every b. Visit a in the outer loop and b in the inner loop.
Call problem_at_bends(float(a),float(b),settings) and return a dictionary with
IDs grid_i_j. A count of 3 per axis produces 9 candidates.

shorten_route(path,edge_checker) obtains a new list with
validate_shortening_inputs. For each internal point, use segment_length to
compute the saving from removing it. Check the replacement segment with
checked_edge(edge_checker,left,right). Choose the permitted removal with the
greatest saving strictly above 1e-12 m. Keep the leftmost on an exact saving tie.
Remove that one point and restart. Stop when no permitted improvement remains.
Return a new Path while preserving the endpoints and the input path.
The raw length can exceed the limit. Check the final route after shortening.

select_shortest(results) looks at the supplied evaluation records.
Ignore records with an error, no report or report.valid=False.
Return the ID with the smallest report.metrics.length_m among accepted records.
Keep the first ID on an exact length tie. Return None if no route is accepted.
Do not modify the result records.

The untouched starter reports **42 failed and 21 passed** because these three
bodies raise NotImplementedError. Import or environment errors are not expected.
After completing them, run:

```bat
python -m pytest tests/public tests/test_student.py -q
python -m ap_week06
python examples/compare_grids.py
python scripts/verify_submission.py
```

The supplied 60 public checks and three basic checks give **63 passed**.
The checker should report LOCAL CHECK PASS. It checks local files and tests.
GitHub and LMS submission remain separate steps.

The application generates 17 x 17 = 289 candidates and selects grid_5_11.
Its shortened path is (0,0), (2,-0.6), (4,0.6), (6,0), approximately.
The raw length is 7.532381 m and the final length is 6.508503 m.
The geometric replay reaches (6,0). It is not a physics simulation.

compare_grids.py holds the scene and constraints fixed. Nine values per axis
give 81 candidates and no accepted route. Seventeen give 289 candidates and
one accepted route. A failed coarse grid does not prove that no route exists.

Saving artifacts/candidate_comparison.json is handled by the supplied program.
You do not need to implement or edit records, deletion history or a JSON schema.
To view the stored winner, you may run:

```bat
python scripts/render_selection.py
```

The supplied renderer writes artifacts/candidate_selection.svg. Open it in a
browser to compare the raw dashed path with the final solid path.
The generated JSON and SVG are ignored by Git. No separate report, log,
screenshot or generated-file submission is required.

## 5. Push and submit

Use your private Week 6 repository and invite the exact SSUMechE account.
A correctly addressed invitation sent on time may remain pending until the
instructor accepts it. That alone is not a missing submission.

```bat
git status --short
git diff
git add src/ap_week06/selection.py
git diff --staged
git commit -m "Complete Week 6 route improvement"
git push origin main
git status --short
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Press q to leave a diff pager. Final status must be empty.
Match the full local and remote commit IDs and inspect the pushed revision
on GitHub.

Within one week of the lab, by Wednesday 11:59 PM on the Week 6 date announced
in LMS, submit these two items:

- Your own repository URL.
- The full 40-character commit ID of the pushed revision.

Private visibility and SSUMechE access are checked separately. LMS needs no
confirmation sentence, ZIP, screenshot, report or generated file. GitHub upload
alone is not LMS submission. Later pushes do not replace the submitted commit.
Week 7 continuity does not postpone this week's submission. Preserve the
announced mandatory-submission zero-point rule and the timely-pending exception.
A failed numerical test alone is not automatic zero for the entire Assignment.
