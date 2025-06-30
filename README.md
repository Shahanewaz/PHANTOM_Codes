# PHANTOM: Prompt-based Human Attribute Navigation for Targeted Obfuscation with Multimodal Large Language Models
This repository contains the codebase for the manuscript titled **"PHANTOM: Prompt-based Human Attribute Navigation for Targeted Obfuscation with Multimodal Large Language Models."**

In this framework, we consider an attacker image (referred to as the *source image* in the manuscript) and a victim image (the *target image* in the manuscript). The purpose of PHANTOM is to generate an intermediate image that an attacker can use to effectively impersonate the victim by systematically modifying human attributes guided by multimodal large language models.

<div style="text-align: center;">

  <figure style="
      display: inline-block;
      width: 45%;
      margin: 0 1em;
      vertical-align: top;
      text-align: center;  
  ">
    <img src="Figures/ex1.png"
         alt="Impersonation within the same gender"
         style="width: 100%;">
    <figcaption style="font-style: italic; margin-top: 0.5em;">
      (a) Impersonation within the same gender
    </figcaption>
  </figure>

  <figure style="
      display: inline-block;
      width: 45%;
      margin: 0 1em;
      vertical-align: top;
      text-align: center;  
  ">
    <img src="Figures/ex2.png"
         alt="Impersonation with different genders"
         style="width: 100%;">
    <figcaption style="font-style: italic; margin-top: 0.5em;">
      (b) Impersonation with different genders
    </figcaption>
  </figure>

</div>

<p align="center" style="font-style: bold;">
  Figure 1. PHANTOM-generated impersonation attacks in same-gender (a) and different-gender (b) scenarios.
</p>

# Flowchart of PHANTOM

PHANTOM is operated through the following sequence of integrated modules:

- **Initialization Module:** Each iteration in PHANTOM begins with the current updated image, along with the fixed source and target images.

- **Analysis Module:** Next, PHANTOM compares the source and target images using the LLM, identifying key visual differences (e.g., facial structure, hairstyle, skin tone, background) and translating them into precise editing instructions. It also evaluates how each change affects SSIM to prioritize edits that better align the source with the target.

- **Prompt-Guided Update Module:** At this module, the LLM generates an updated image based on the latest edit instructions. PHANTOM then evaluates its SSIM, and if the result satisfies the imposed constraints, the image is accepted for the next editing round.

We will show the flowchart below.

<p align="center">
  <img src="Figures/flowchart.PNG" alt="flowchart of PHANTOM" width="65%">
</p>

<p align="center" style="font-style: bold;">
  Figure 2. A single iteration of the PHANTOM framework.
</p>

# Folder Structure

```
├── Codebase
│ ├── GPT4o
│ │ ├── config.py
│ │ └── image_utils.py
│ │ └── main.py
│ │ └── openai_services.py
│ └── select_llm.py
```

# Usage Instructions

To implement the methodology described, execute the following script with the specified number of iterations.

<p align="center">
  <code>python select_llm.py</code>
</p>
