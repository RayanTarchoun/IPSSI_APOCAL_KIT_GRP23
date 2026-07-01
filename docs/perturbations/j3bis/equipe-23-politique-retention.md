# Politique de rétention et de protection des données personnelles

**Équipe 23 — EduTutor IA** · Perturbation J3-bis (RGPD) · v1.0 · 01/07/2026

> Document de conformité (POC pédagogique). Le responsable de traitement est
> l'équipe projet EduTutor IA ; contact DPO (fictif) : **dpo@edututor-ia.example**.

Cette politique décrit **quelles données** sont conservées, **combien de temps**,
**sur quelle base légale**, et **comment** elles sont supprimées. Elle répond au
droit d'accès (Art. 15) exercé via l'export `GET /api/accounts/me/export/`.

---

## 1. Durées de conservation par type de donnée

| Catégorie | Données concernées | Durée de conservation | Point de départ |
|-----------|--------------------|-----------------------|-----------------|
| Compte utilisateur | email, nom, prénom, identifiant, mot de passe (haché) | Durée du compte, puis **suppression immédiate** à la clôture | Dernière activité |
| Documents importés | texte source des cours (PDF/collé) | Durée du compte, ou suppression à la demande | Import |
| Quiz générés | quiz, questions, options, bonne réponse | Durée du compte | Génération |
| Réponses & scores | réponses choisies, score /10 | Durée du compte | Passage du quiz |
| Journal des demandes RGPD (`DataRequest`) | qui, quand, statut, empreinte du fichier | **3 ans** (preuve de conformité) | Date de la demande |
| Logs techniques applicatifs | horodatage, endpoint, code retour | **12 mois** glissants | Émission du log |

> Les comptes **inactifs depuis 24 mois** font l'objet d'une notification puis
> d'une suppression (principe de **minimisation** et de **limitation de conservation**,
> Art. 5.1.e du RGPD).

## 2. Base légale des traitements (Art. 6 RGPD)

| Traitement | Base légale (Art. 6) |
|------------|----------------------|
| Création et gestion du compte | **Art. 6.1.b** — exécution du contrat (fourniture du service) |
| Génération et conservation des quiz / scores | **Art. 6.1.b** — exécution du contrat |
| Journal des demandes RGPD (audit trail) | **Art. 6.1.c** — obligation légale (démontrer la conformité) |
| Logs techniques (sécurité, débogage) | **Art. 6.1.f** — intérêt légitime (sécurité du service) |
| Envoi d'emails de validation / réinitialisation | **Art. 6.1.b** — exécution du contrat |

Aucune donnée n'est utilisée à des fins de prospection ni cédée à des tiers.
En cas de recours à un fournisseur LLM **cloud**, le texte du cours peut être
transmis au sous-traitant : le mode **local (Ollama)** est le défaut souverain
(cf. [ADR Prompt Injection](../../adr/equipe-23-adr-prompt-injection.md) et Note de sécurité §4.4).

## 3. Modalités d'exercice des droits et de suppression (Art. 15 à 20)

- **Droit d'accès (Art. 15)** et **portabilité (Art. 20)** : bouton
  « Exporter mes données » (profil) → export **JSON** ou **CSV** structuré,
  incluant les 6 catégories. Endpoint : `GET /api/accounts/me/export/?fmt=json|csv`.
- **Droit de rectification (Art. 16)** : modification du prénom / nom / email
  depuis la page profil.
- **Droit à l'effacement (Art. 17)** : bouton « Supprimer définitivement mon
  compte » → suppression **dure** en cascade (compte, quiz, questions, réponses,
  tokens) via `on_delete=CASCADE`. Effet immédiat, irréversible.
- **Droit à la limitation (Art. 18)** : sur demande au DPO, gel du traitement.
- **Délai de réponse** : **1 mois maximum** (Art. 12.3) ; dans le POC, l'export
  est **instantané** et **auto-servi**.

### Sécurité et traçabilité

- Chaque export est **journalisé** dans `DataRequest` avec l'**empreinte SHA-256**
  du fichier remis (preuve d'intégrité).
- Les exports sont **strictement filtrés par utilisateur** (`request.user`) : aucune
  donnée d'un autre compte ne peut apparaître (testé, cf. `accounts/test_export.py`).
- Les mots de passe ne sont jamais exportés en clair (hachés en base, hors périmètre d'export).

---

*Version 1.0 — à réviser annuellement ou à chaque évolution du traitement.*
