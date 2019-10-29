Example Reflow Profiles for esp-reflow Project
==============================================

The files in this directory should be copied to the root of the SD card.

Each file describes a distinct reflow profile curve. They can be easily
extended by custom profiles. The filename extension should be '.prf'.

The file format can be described as follows:

```
Profile Name
1st Temperature Setpoint, Soaking Time, Overshoot Prevention Strength
2nd Temperature Setpoint, Soaking Time, Overshoot Prevention Strength
...
Nth Temperature Setpoint, Soaking Time, Overshoot Prevention Strength
```

The file may contain whitespace but must not be larger than 250 bytes.

For example, the file `Sn63Pb37.prf` describes the reflow curve for a
solder paste that contains a metallic alloy of 63% tin and 37% lead:

```
Sn63Pb37
155,80,3
220,60,2
```

- The first line denotes that the profile is named `Sn63Pb`.
- The second line instructs to heat up to `155°C` and then soak at that
  temperature for `80` seconds. While narrowing in on the setpoint of
  `155°C` there should be `3` overshoot prevention steps (i.e. gradual
  lowering of heater output)
- The third line instructs to heat up to `220°C` and soak for 60 seconds
  with `2` overshoot prevention steps
- If the last soaking phase is over, the oven will turn off
  automatically and ring the buzzer to notify of the end of the reflow
  process
