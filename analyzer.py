def generate_single_judge_stats(self, judge_name, cases):
        """Generate statistics for a single judge"""
        if not cases:
            return f"No cases found for {judge_name}\n"
        
        stats = f"JUDGE STATISTICS: {judge_name}\n"
        stats += f"{'='*60}\n\n"
        
        total = len(cases)
        guilty = sum(1 for case in cases if case['verdict'] == 'Guilty')
        not_guilty = sum(1 for case in cases if case['verdict'] == 'Not Guilty')
        plea_deals = sum(1 for case in cases if case['verdict'] == 'Plea Deal')
        
        guilty_rate = (guilty / total * 100) if total > 0 else 0
        
        stats += f"Total Cases Analyzed: {total}\n"
        stats += f"Conviction Rate: {guilty_rate:.1f}%\n\n"
        
        stats += f"Verdict Breakdown:\n"
        stats += f"- Guilty: {guilty} ({guilty/total*100:.1f}%)\n"
        stats += f"- Not Guilty: {not_guilty} ({not_guilty/total*100:.1f}%)\n"
        stats += f"- Plea Deals: {plea_deals} ({plea_deals/total*100:.1f}%)\n\n"
        
        # Analyze sentences
        sentences = []
        probation_count = 0
        prison_count = 0
        
        for case in cases:
            if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                # Check for prison time
                years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                if years_match:
                    sentences.append(int(years_match.group(1)))
                    prison_count += 1
                elif 'probation' in case['sentence'].lower():
                    probation_count += 1
        
        if sentences:
            avg_sentence = sum(sentences) / len(sentences)
            stats += f"Sentencing Patterns (for guilty verdicts):\n"
            stats += f"- Average Prison Sentence: {avg_sentence:.1f} years\n"
            stats += f"- Minimum Sentence: {min(sentences)} years\n"
            stats += f"- Maximum Sentence: {max(sentences)} years\n"
            stats += f"- Prison Sentences: {prison_count}\n"
            stats += f"- Probation Only: {probation_count}\n\n"
        
        # Analyze case types
        case_types = {}
        for case in cases:
            case_type = case['charge']
            if case_type not in case_types:
                case_types[case_type] = {'total': 0, 'guilty': 0}
            case_types[case_type]['total'] += 1
            if case['verdict'] == 'Guilty':
                case_types[case_type]['guilty'] += 1
        
        stats += f"Case Types Handled:\n"
        for case_type, data in sorted(case_types.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
            conviction_rate = (data['guilty'] / data['total'] * 100) if data['total'] > 0 else 0
            stats += f"- {case_type}: {data['total']} cases ({conviction_rate:.1f}% conviction rate)\n"
        
        stats += f"\n{'='*60}\n"
        stats += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        return stats"""
Case analysis and prediction engine for criminal cases
"""
import re
import config

class CaseAnalyzer:
    """Analyzes cases and generates predictions"""
    
    def __init__(self):
        self.similar_cases = []
        
    def find_similar_cases(self, case_database, client_info, max_results=50):
        """
        Find cases similar to the client's situation
        
        Args:
            case_database: List of all cases
            client_info: Dict with client's information
            max_results: Maximum number of similar cases to return
            
        Returns:
            list: Similar cases sorted by relevance
        """
        similar_cases = []
        
        for case in case_database:
            similarity_score = self._calculate_similarity(case, client_info)
            
            if similarity_score > 0:
                similar_cases.append((similarity_score, case))
        
        # Sort by similarity score (highest first)
        similar_cases.sort(key=lambda x: x[0], reverse=True)
        
        # Return just the cases (without scores)
        self.similar_cases = [case for _, case in similar_cases[:max_results]]
        return self.similar_cases
    
    def _calculate_similarity(self, case, client_info):
        """Calculate similarity score between a case and client situation"""
        score = 0
        weights = config.SIMILARITY_WEIGHTS
        
        # Match charge type
        client_charge = client_info['charge']
        if client_charge.lower() in case['charge'].lower() or case['charge'].lower() in client_charge.lower():
            score += weights['charge_match']
        
        # Match criminal history
        if abs(case['prior_felonies'] - client_info['felonies']) <= 1:
            score += weights['felony_match']
        if abs(case['prior_misdemeanors'] - client_info['misdemeanors']) <= 2:
            score += weights['misdemeanor_match']
        if abs(case['prior_convictions'] - client_info['convictions']) <= 2:
            score += weights['conviction_match']
            
        # Match judge if specified
        if client_info.get('judge') and case['judge'] == client_info['judge']:
            score += weights['judge_match']
        
        return score
    
    def generate_prediction_report(self, client_info):
        """
        Generate comprehensive prediction report
        
        Args:
            client_info: Dict with client's information
            
        Returns:
            str: Formatted prediction report
        """
        if not self.similar_cases:
            return "No similar cases found in the database.\n"
        
        # Calculate statistics
        stats = self._calculate_statistics()
        
        # Generate report sections
        report = self._generate_header(client_info)
        report += self._generate_verdict_analysis(stats)
        report += self._generate_sentencing_analysis(stats)
        report += self._generate_risk_assessment(stats)
        report += self._generate_criminal_history_impact(client_info)
        report += self._generate_judge_analysis(client_info)
        report += self._generate_recommendations(stats)
        report += self._generate_disclaimer(stats)
        
        return report
    
    def _calculate_statistics(self):
        """Calculate statistics from similar cases"""
        total_cases = len(self.similar_cases)
        
        stats = {
            'total_cases': total_cases,
            'guilty_count': sum(1 for case in self.similar_cases if case['verdict'] == 'Guilty'),
            'not_guilty_count': sum(1 for case in self.similar_cases if case['verdict'] == 'Not Guilty'),
            'plea_count': sum(1 for case in self.similar_cases if case['verdict'] == 'Plea Deal'),
            'sentences': []
        }
        
        # Calculate rates
        stats['guilty_rate'] = (stats['guilty_count'] / total_cases * 100) if total_cases > 0 else 0
        stats['not_guilty_rate'] = (stats['not_guilty_count'] / total_cases * 100) if total_cases > 0 else 0
        stats['plea_rate'] = (stats['plea_count'] / total_cases * 100) if total_cases > 0 else 0
        
        # Extract sentences
        for case in self.similar_cases:
            if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                if years_match:
                    stats['sentences'].append(int(years_match.group(1)))
        
        return stats
    
    def _generate_header(self, client_info):
        """Generate report header"""
        report = f"CASE OUTCOME PREDICTION REPORT\n"
        report += f"{'='*60}\n\n"
        
        report += f"Client Profile:\n"
        report += f"- Current Charge: {client_info['charge']}\n"
        report += f"- Prior Felonies: {client_info['felonies']}\n"
        report += f"- Prior Misdemeanors: {client_info['misdemeanors']}\n"
        report += f"- Total Prior Convictions: {client_info['convictions']}\n"
        if client_info.get('judge'):
            report += f"- Assigned Judge: {client_info['judge']}\n"
        report += f"\n"
        
        return report
    
    def _generate_verdict_analysis(self, stats):
        """Generate verdict probability analysis"""
        report = f"Analysis Based on {stats['total_cases']} Similar Cases:\n"
        report += f"{'='*60}\n\n"
        
        report += f"VERDICT PROBABILITIES:\n"
        report += f"- Guilty: {stats['guilty_rate']:.1f}% ({stats['guilty_count']} cases)\n"
        report += f"- Not Guilty: {stats['not_guilty_rate']:.1f}% ({stats['not_guilty_count']} cases)\n"
        report += f"- Plea Deal: {stats['plea_rate']:.1f}% ({stats['plea_count']} cases)\n\n"
        
        return report
    
    def _generate_sentencing_analysis(self, stats):
        """Generate sentencing analysis"""
        if not stats['sentences']:
            return ""
            
        avg_sentence = sum(stats['sentences']) / len(stats['sentences'])
        min_sentence = min(stats['sentences'])
        max_sentence = max(stats['sentences'])
        
        report = f"SENTENCING ANALYSIS (for guilty verdicts):\n"
        report += f"- Average Sentence: {avg_sentence:.1f} years\n"
        report += f"- Minimum Sentence: {min_sentence} years\n"
        report += f"- Maximum Sentence: {max_sentence} years\n"
        report += f"- Based on {len(stats['sentences'])} cases with prison sentences\n\n"
        
        return report
    
    def _generate_risk_assessment(self, stats):
        """Generate risk assessment"""
        report = f"RISK ASSESSMENT:\n"
        
        if stats['guilty_rate'] > config.HIGH_RISK_THRESHOLD:
            report += f"⚠️ HIGH RISK: {stats['guilty_rate']:.1f}% conviction rate in similar cases\n"
            report += f"   Strong recommendation to consider plea negotiations\n"
        elif stats['guilty_rate'] > config.MODERATE_RISK_THRESHOLD:
            report += f"⚡ MODERATE RISK: {stats['guilty_rate']:.1f}% conviction rate in similar cases\n"
            report += f"   Consider both trial and plea options carefully\n"
        else:
            report += f"✅ LOWER RISK: {stats['guilty_rate']:.1f}% conviction rate in similar cases\n"
            report += f"   Trial may be a viable option\n"
        
        return report + "\n"
    
    def _generate_criminal_history_impact(self, client_info):
        """Analyze impact of criminal history"""
        report = f"CRIMINAL HISTORY IMPACT:\n"
        
        # Find cases with similar criminal history
        similar_history_cases = [
            case for case in self.similar_cases 
            if abs(case['prior_felonies'] - client_info['felonies']) <= 1
        ]
        
        if similar_history_cases:
            similar_guilty = sum(1 for case in similar_history_cases if case['verdict'] == 'Guilty')
            similar_rate = (similar_guilty / len(similar_history_cases)) * 100
            report += f"- Defendants with similar criminal history: {similar_rate:.1f}% conviction rate\n"
            
            # Compare sentences
            history_sentences = []
            for case in similar_history_cases:
                if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                    years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                    if years_match:
                        history_sentences.append(int(years_match.group(1)))
            
            if history_sentences:
                avg_history_sentence = sum(history_sentences) / len(history_sentences)
                report += f"- Average sentence for similar criminal history: {avg_history_sentence:.1f} years\n"
        
        return report
    
    def _generate_judge_analysis(self, client_info):
        """Generate judge-specific analysis"""
        if not client_info.get('judge'):
            return ""
            
        judge_cases = [case for case in self.similar_cases if case['judge'] == client_info['judge']]
        
        if not judge_cases:
            return ""
            
        judge_guilty = sum(1 for case in judge_cases if case['verdict'] == 'Guilty')
        judge_rate = (judge_guilty / len(judge_cases)) * 100
        
        report = f"\nJUDGE-SPECIFIC ANALYSIS ({client_info['judge']}):\n"
        report += f"- Conviction rate for similar cases: {judge_rate:.1f}%\n"
        report += f"- Based on {len(judge_cases)} similar cases before this judge\n"
        
        return report
    
    def _generate_recommendations(self, stats):
        """Generate recommendations based on analysis"""
        report = f"\nRECOMMENDATIONS:\n"
        report += f"{'='*60}\n"
        
        if stats['guilty_rate'] > config.HIGH_RISK_THRESHOLD:
            report += "1. Strongly consider plea negotiations\n"
            report += "2. Focus on mitigation factors and sentencing alternatives\n"
            report += "3. Prepare comprehensive character references\n"
        elif stats['guilty_rate'] > config.MODERATE_RISK_THRESHOLD:
            report += "1. Evaluate strength of prosecution's evidence carefully\n"
            report += "2. Consider both plea and trial options\n"
            report += "3. Focus on reasonable doubt arguments\n"
        else:
            report += "1. Trial appears to be a viable option\n"
            report += "2. Focus on weaknesses in prosecution's case\n"
            report += "3. Consider aggressive defense strategy\n"
        
        return report
    
    def _generate_disclaimer(self, stats):
        """Generate disclaimer"""
        report = f"\nDISCLAIMER: This analysis is based on {stats['total_cases']} similar cases found in\n"
        report += "Google Scholar. Actual outcomes may vary. Always consult with your attorney\n"
        report += "for legal advice specific to your case.\n"
        
        return report
    
    def generate_judge_statistics(self, judges_data):
        """Generate statistics report for all judges"""
        if not judges_data:
            return "No judge data available.\n"
        
        stats = f"JUDGE STATISTICS REPORT\n"
        stats += f"{'='*60}\n\n"
        
        # Sort judges by number of cases
        sorted_judges = sorted(judges_data.items(), key=lambda x: len(x[1]), reverse=True)
        
        for judge, cases in sorted_judges[:config.MAX_JUDGES_DISPLAY]:
            total = len(cases)
            guilty = sum(1 for case in cases if case['verdict'] == 'Guilty')
            not_guilty = sum(1 for case in cases if case['verdict'] == 'Not Guilty')
            plea_deals = sum(1 for case in cases if case['verdict'] == 'Plea Deal')
            
            guilty_rate = (guilty / total * 100) if total > 0 else 0
            
            stats += f"{judge}\n"
            stats += f"- Total Cases: {total}\n"
            stats += f"- Conviction Rate: {guilty_rate:.1f}%\n"
            stats += f"- Guilty: {guilty}, Not Guilty: {not_guilty}, Plea Deals: {plea_deals}\n"
            
            # Average sentence length
            sentences = []
            for case in cases:
                if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                    years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                    if years_match:
                        sentences.append(int(years_match.group(1)))
            
            if sentences:
                avg_sentence = sum(sentences) / len(sentences)
                stats += f"- Average Sentence: {avg_sentence:.1f} years\n"
            
            stats += f"{'-'*40}\n\n"
        
        return stats
    
    def generate_prediction_report(self, client_info):
        """
        Generate comprehensive prediction report
        
        Args:
            client_info: Dict with client's information
            
        Returns:
            str: Formatted prediction report
        """
        if not self.similar_cases:
            return "No similar cases found in the database.\n"
        
        # Calculate statistics
        stats = self._calculate_statistics()
        
        # Generate report sections
        report = self._generate_header(client_info)
        report += self._generate_verdict_analysis(stats)
        report += self._generate_sentencing_analysis(stats)
        report += self._generate_risk_assessment(stats)
        report += self._generate_criminal_history_impact(client_info)
        report += self._generate_judge_analysis(client_info)
        report += self._generate_recommendations(stats)
        report += self._generate_disclaimer(stats)
        
        return report
    
    def _calculate_statistics(self):
        """Calculate statistics from similar cases"""
        total_cases = len(self.similar_cases)
        
        stats = {
            'total_cases': total_cases,
            'guilty_count': sum(1 for case in self.similar_cases if case['verdict'] == 'Guilty'),
            'not_guilty_count': sum(1 for case in self.similar_cases if case['verdict'] == 'Not Guilty'),
            'plea_count': sum(1 for case in self.similar_cases if case['verdict'] == 'Plea Deal'),
            'sentences': []
        }
        
        # Calculate rates
        stats['guilty_rate'] = (stats['guilty_count'] / total_cases * 100) if total_cases > 0 else 0
        stats['not_guilty_rate'] = (stats['not_guilty_count'] / total_cases * 100) if total_cases > 0 else 0
        stats['plea_rate'] = (stats['plea_count'] / total_cases * 100) if total_cases > 0 else 0
        
        # Extract sentences
        for case in self.similar_cases:
            if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                if years_match:
                    stats['sentences'].append(int(years_match.group(1)))
        
        return stats
    
    def _generate_header(self, client_info):
        """Generate report header"""
        report = f"CASE OUTCOME PREDICTION REPORT\n"
        report += f"{'='*60}\n\n"
        
        report += f"Client Profile:\n"
        report += f"- Current Charge: {client_info['charge']}\n"
        report += f"- Prior Felonies: {client_info['felonies']}\n"
        report += f"- Prior Misdemeanors: {client_info['misdemeanors']}\n"
        report += f"- Total Prior Convictions: {client_info['convictions']}\n"
        if client_info.get('judge'):
            report += f"- Assigned Judge: {client_info['judge']}\n"
        report += f"\n"
        
        return report
    
    def _generate_verdict_analysis(self, stats):
        """Generate verdict probability analysis"""
        report = f"Analysis Based on {stats['total_cases']} Similar Cases:\n"
        report += f"{'='*60}\n\n"
        
        report += f"VERDICT PROBABILITIES:\n"
        report += f"- Guilty: {stats['guilty_rate']:.1f}% ({stats['guilty_count']} cases)\n"
        report += f"- Not Guilty: {stats['not_guilty_rate']:.1f}% ({stats['not_guilty_count']} cases)\n"
        report += f"- Plea Deal: {stats['plea_rate']:.1f}% ({stats['plea_count']} cases)\n\n"
        
        return report
    
    def _generate_sentencing_analysis(self, stats):
        """Generate sentencing analysis"""
        if not stats['sentences']:
            return ""
            
        avg_sentence = sum(stats['sentences']) / len(stats['sentences'])
        min_sentence = min(stats['sentences'])
        max_sentence = max(stats['sentences'])
        
        report = f"SENTENCING ANALYSIS (for guilty verdicts):\n"
        report += f"- Average Sentence: {avg_sentence:.1f} years\n"
        report += f"- Minimum Sentence: {min_sentence} years\n"
        report += f"- Maximum Sentence: {max_sentence} years\n"
        report += f"- Based on {len(stats['sentences'])} cases with prison sentences\n\n"
        
        return report
    
    def _generate_risk_assessment(self, stats):
        """Generate risk assessment"""
        report = f"RISK ASSESSMENT:\n"
        
        if stats['guilty_rate'] > 75:
            report += f"⚠️ HIGH RISK: {stats['guilty_rate']:.1f}% conviction rate in similar cases\n"
            report += f"   Strong recommendation to consider plea negotiations\n"
        elif stats['guilty_rate'] > 50:
            report += f"⚡ MODERATE RISK: {stats['guilty_rate']:.1f}% conviction rate in similar cases\n"
            report += f"   Consider both trial and plea options carefully\n"
        else:
            report += f"✅ LOWER RISK: {stats['guilty_rate']:.1f}% conviction rate in similar cases\n"
            report += f"   Trial may be a viable option\n"
        
        return report + "\n"
    
    def _generate_criminal_history_impact(self, client_info):
        """Analyze impact of criminal history"""
        report = f"CRIMINAL HISTORY IMPACT:\n"
        
        # Find cases with similar criminal history
        similar_history_cases = [
            case for case in self.similar_cases 
            if abs(case['prior_felonies'] - client_info['felonies']) <= 1
        ]
        
        if similar_history_cases:
            similar_guilty = sum(1 for case in similar_history_cases if case['verdict'] == 'Guilty')
            similar_rate = (similar_guilty / len(similar_history_cases)) * 100
            report += f"- Defendants with similar criminal history: {similar_rate:.1f}% conviction rate\n"
            
            # Compare sentences
            history_sentences = []
            for case in similar_history_cases:
                if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                    years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                    if years_match:
                        history_sentences.append(int(years_match.group(1)))
            
            if history_sentences:
                avg_history_sentence = sum(history_sentences) / len(history_sentences)
                report += f"- Average sentence for similar criminal history: {avg_history_sentence:.1f} years\n"
        
        return report
    
    def _generate_judge_analysis(self, client_info):
        """Generate judge-specific analysis"""
        if not client_info.get('judge'):
            return ""
            
        judge_cases = [case for case in self.similar_cases if case['judge'] == client_info['judge']]
        
        if not judge_cases:
            return ""
            
        judge_guilty = sum(1 for case in judge_cases if case['verdict'] == 'Guilty')
        judge_rate = (judge_guilty / len(judge_cases)) * 100
        
        report = f"\nJUDGE-SPECIFIC ANALYSIS ({client_info['judge']}):\n"
        report += f"- Conviction rate for similar cases: {judge_rate:.1f}%\n"
        report += f"- Based on {len(judge_cases)} similar cases before this judge\n"
        
        return report
    
    def _generate_recommendations(self, stats):
        """Generate recommendations based on analysis"""
        report = f"\nRECOMMENDATIONS:\n"
        report += f"{'='*60}\n"
        
        if stats['guilty_rate'] > 70:
            report += "1. Strongly consider plea negotiations\n"
            report += "2. Focus on mitigation factors and sentencing alternatives\n"
            report += "3. Prepare comprehensive character references\n"
        elif stats['guilty_rate'] > 50:
            report += "1. Evaluate strength of prosecution's evidence carefully\n"
            report += "2. Consider both plea and trial options\n"
            report += "3. Focus on reasonable doubt arguments\n"
        else:
            report += "1. Trial appears to be a viable option\n"
            report += "2. Focus on weaknesses in prosecution's case\n"
            report += "3. Consider aggressive defense strategy\n"
        
        return report
    
    def _generate_disclaimer(self, stats):
        """Generate disclaimer"""
        report = f"\nDISCLAIMER: This analysis is based on {stats['total_cases']} similar cases found in\n"
        report += "Google Scholar. Actual outcomes may vary. Always consult with your attorney\n"
        report += "for legal advice specific to your case.\n"
        
        return report
    
    def generate_judge_statistics(self, judges_data):
        """Generate statistics report for all judges"""
        if not judges_data:
            return "No judge data available.\n"
        
        stats = f"JUDGE STATISTICS REPORT\n"
        stats += f"{'='*60}\n\n"
        
        # Sort judges by number of cases
        sorted_judges = sorted(judges_data.items(), key=lambda x: len(x[1]), reverse=True)
        
        for judge, cases in sorted_judges[:20]:  # Top 20 judges
            total = len(cases)
            guilty = sum(1 for case in cases if case['verdict'] == 'Guilty')
            not_guilty = sum(1 for case in cases if case['verdict'] == 'Not Guilty')
            plea_deals = sum(1 for case in cases if case['verdict'] == 'Plea Deal')
            
            guilty_rate = (guilty / total * 100) if total > 0 else 0
            
            stats += f"{judge}\n"
            stats += f"- Total Cases: {total}\n"
            stats += f"- Conviction Rate: {guilty_rate:.1f}%\n"
            stats += f"- Guilty: {guilty}, Not Guilty: {not_guilty}, Plea Deals: {plea_deals}\n"
            
            # Average sentence length
            sentences = []
            for case in cases:
                if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                    years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                    if years_match:
                        sentences.append(int(years_match.group(1)))
            
            if sentences:
                avg_sentence = sum(sentences) / len(sentences)
                stats += f"- Average Sentence: {avg_sentence:.1f} years\n"
            
            stats += f"{'-'*40}\n\n"
        
        return stats
