This is named manager to give the idea that this resembles a django manager-y access to the core models for clinical data interactions.

Programming and developing these APIs should follow this workflow:
1:  Develop the appropriate, non stupid model access/management in the requisite apps' managers.
2:  When access across models and processing is needed, develop it here.