# Nose Print Biometric Identification – Tanzania

An open-source proof of concept (PoC) for livestock nose-print image capture, registration, storage and candidate identification using pretrained computer-vision models.

**Status:** Early PoC / research prototype — not approved for production or legal identity decisions.

## Goals

- Capture nose/muzzle images from a computer webcam or an Android phone browser.
- Register an animal with multiple reference images (recommended: 3–5 varied, sharp images).
- Store original images and model-versioned feature embeddings.
- Compare a new scan against registered references and return a candidate animal or **Unknown**.
- Evaluate performance on public data before any field deployment.

## Proposed architecture

- **UI:** Streamlit (browser camera capture; Android remote access requires HTTPS).
- **API:** FastAPI.
- **Computer vision:** PyTorch + TorchVision pretrained ResNet18 baseline.
- **Database:** PostgreSQL + pgvector.
- **Image storage:** Local filesystem for this PoC; production storage must be secured and backed up.

The initial ResNet18 model is a generic ImageNet feature extractor, **not a validated nose-print biometric model**. Similarity scores are not probabilities and must not be treated as proof of identity.

## Repository roadmap

1. Project foundation, configuration and local development environment.
2. PostgreSQL schema with pgvector and model-versioned embeddings.
3. Image preprocessing and pretrained embedding extraction.
4. Animal registration with multiple images.
5. Nose-print candidate identification and Unknown rejection.
6. Streamlit capture UI for desktop webcam and Android browser.
7. Evaluation: animal-disjoint splits, FAR, FRR, EER and Rank-1 accuracy.
8. Security, audit trail, documentation and deployment hardening.

## Quick start

The runnable application setup will be added in subsequent implementation commits. See the project documentation as the PoC is built.

## Data and research notes

A public cattle muzzle/nose-print dataset has been identified as a possible starting point. Before downloading, using or redistributing it, verify its current license and terms. Dataset conditions may differ significantly from Tanzanian field, market and auction environments.

For credible evaluation:
- Keep all images of a given animal in only one data split.
- Where possible, separate capture sessions between training/reference and testing.
- Calibrate the match threshold on validation data; do not assume a universal cosine threshold.
- Report false acceptance and false rejection rates, not only overall accuracy.
- Include an **Unknown** outcome and human review for uncertain matches.

## Responsible use

This prototype is for research and technical feasibility testing. A match must not be used alone to establish ownership, support enforcement, or make an irreversible decision. Production use requires field validation, privacy and data-protection review, access control, encryption, audit logging, retention rules and operational security.

## License

A license will be selected and added after reviewing the intended dataset and contribution model. Until then, no reuse license is granted by this repository.
