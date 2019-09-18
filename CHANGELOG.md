# Transmorgopy Changelog
## 1.1.9- 2019-09-18
### Changed
* added whitespace after assignment
## 1.1.8- 2018-11-12
### Added
* improved the early return detection mechanism and incorporated in standard rules
* floor and ceil rules
### Changed
* reworked the `Segment` class to better accommodate raw strings
* clearer partial support for `Segement`
### Fixed
* removed `talos_star` part from the `Prewords` class, it is now a default for the `pre_parts` arg.
* early return detection in strings and comments fixed.
* bad if/ while rules on uppercase keywords.
## 1.1.7- 2018-10-03 
### Added
* This changelog
* README
* Raw strings can now be added to segments without pre-adding it
* kw arguments for both `convert` and `rules` for raw parts in segments 
### Changed
* The `talos_star` part can now be explicitly removed/changed with the `pre_parts` arg
* Split the Result rule to two rules depending on behaviour
* the `header` keyword argument has been changed to `disclose`
* `try` mode no longer issues a warning when switching to var
### Fix
* bug on detecting result
