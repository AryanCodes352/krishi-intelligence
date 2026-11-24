def get_crop_stage(crop: str, days_after_sowing: int) -> str:
    if crop.lower() == 'wheat':
        if days_after_sowing <= 10: return 'Germination'
        if days_after_sowing <= 25: return 'Seedling'
        if days_after_sowing <= 45: return 'Tillering'
        if days_after_sowing <= 65: return 'Jointing'
        if days_after_sowing <= 80: return 'Booting'
        if days_after_sowing <= 90: return 'Heading/Flowering'
        if days_after_sowing <= 115: return 'Grain Filling'
        if days_after_sowing <= 140: return 'Maturity'
        return 'Post-harvest'
    return 'Unknown'
