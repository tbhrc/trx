"""
Performance Benchmark for NewsEngine (v1.2.3)

This script benchmarks the performance of NewsEngine with production-scale data
to validate Phase 5 optimizations and tune cache settings.

Author: AI Trading Copilot Team
Version: 1.0
Date: 2025-12-06
"""

import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.v1_0.core.news import NewsEngine, NewsConfig


class NewsEngineBenchmark:
    """Benchmark suite for NewsEngine performance testing."""
    
    def __init__(self):
        self.results = {}
        
    def generate_test_headlines(self, num_headlines: int, num_instruments: int = 5) -> Path:
        """Generate synthetic headlines for testing.
        
        Args:
            num_headlines: Number of headlines to generate
            num_instruments: Number of unique instruments
            
        Returns:
            Path to generated CSV file
        """
        instruments = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "NAS100"][:num_instruments]
        
        positive_templates = [
            "{} rallies on strong growth data",
            "{} gains momentum with positive sentiment",
            "{} surges as bullish outlook strengthens",
            "Optimistic forecast boosts {} markets",
            "Strong economic data lifts {}"
        ]
        
        negative_templates = [
            "{} falls on weak economic concerns",
            "Bearish sentiment weighs on {}",
            "{} declines amid pessimistic outlook",
            "Risk concerns push {} lower",
            "Weak data triggers {} downturn"
        ]
        
        headlines = []
        start_date = datetime.now() - timedelta(days=3)
        
        for i in range(num_headlines):
            instrument = np.random.choice(instruments)
            template = np.random.choice(positive_templates + negative_templates)
            headline = template.format(instrument.replace("USD", ""))
            
            timestamp = start_date + timedelta(
                hours=np.random.randint(0, 72),
                minutes=np.random.randint(0, 60)
            )
            
            headlines.append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'instrument': instrument,
                'headline': headline
            })
        
        df = pd.DataFrame(headlines)
        df = df.sort_values('timestamp')
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='')
        df.to_csv(temp_file.name, index=False)
        
        print(f"Generated {num_headlines} headlines across {num_instruments} instruments")
        return Path(temp_file.name)
    
    def benchmark_sentiment_score(self, engine: NewsEngine, iterations: int = 1000) -> dict:
        """Benchmark sentiment score calculation.
        
        Args:
            engine: NewsEngine instance
            iterations: Number of iterations
            
        Returns:
            Dictionary with timing results
        """
        print(f"\nBenchmark: Sentiment Score ({iterations} iterations)")
        
        timestamp = pd.Timestamp.now()
        instruments = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "NAS100"]
        
        # Warmup (cache cold)
        for instrument in instruments:
            engine.get_sentiment_score(instrument, timestamp)
        
        # Benchmark with cache (hot)
        start = time.time()
        for i in range(iterations):
            instrument = instruments[i % len(instruments)]
            ts = timestamp - timedelta(hours=i % 24)
            score = engine.get_sentiment_score(instrument, ts)
        hot_time = time.time() - start
        
        # Clear cache and benchmark without cache (cold)
        engine.clear_cache()
        
        start = time.time()
        for i in range(iterations):
            instrument = instruments[i % len(instruments)]
            ts = timestamp - timedelta(hours=i % 24)
            score = engine.get_sentiment_score(instrument, ts)
        cold_time = time.time() - start
        
        results = {
            'iterations': iterations,
            'hot_cache_total': hot_time,
            'hot_cache_per_call': (hot_time / iterations) * 1000,  # ms
            'cold_cache_total': cold_time,
            'cold_cache_per_call': (cold_time / iterations) * 1000,  # ms
            'speedup': cold_time / hot_time if hot_time > 0 else 0
        }
        
        print(f"  Hot cache (total): {hot_time:.3f}s")
        print(f"  Hot cache (per call): {results['hot_cache_per_call']:.2f}ms")
        print(f"  Cold cache (total): {cold_time:.3f}s")
        print(f"  Cold cache (per call): {results['cold_cache_per_call']:.2f}ms")
        print(f"  Speedup: {results['speedup']:.1f}x")
        
        return results
    
    def benchmark_instrument_lookup(self, engine: NewsEngine, iterations: int = 10000) -> dict:
        """Benchmark instrument-specific headline lookup.
        
        Args:
            engine: NewsEngine instance
            iterations: Number of iterations
            
        Returns:
            Dictionary with timing results
        """
        print(f"\nBenchmark: Instrument Lookup ({iterations} iterations)")
        
        timestamp = pd.Timestamp.now()
        instruments = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "NAS100"]
        
        start = time.time()
        for i in range(iterations):
            instrument = instruments[i % len(instruments)]
            # Access indexed data
            if instrument in engine.headlines_by_instrument:
                df = engine.headlines_by_instrument[instrument]
        elapsed = time.time() - start
        
        results = {
            'iterations': iterations,
            'total_time': elapsed,
            'per_lookup': (elapsed / iterations) * 1000000,  # microseconds
        }
        
        print(f"  Total time: {elapsed:.3f}s")
        print(f"  Per lookup: {results['per_lookup']:.2f}μs")
        
        return results
    
    def benchmark_trend_analysis(self, engine: NewsEngine, hours_back: int = 24) -> dict:
        """Benchmark sentiment trend analysis.
        
        Args:
            engine: NewsEngine instance
            hours_back: Hours to analyze
            
        Returns:
            Dictionary with timing results
        """
        print(f"\nBenchmark: Sentiment Trend ({hours_back} hours)")
        
        timestamp = pd.Timestamp.now()
        instruments = ["EURUSD", "GBPUSD", "XAUUSD"]
        
        trends = {}
        start = time.time()
        for instrument in instruments:
            trends[instrument] = engine.get_sentiment_trend(instrument, timestamp, hours_back)
        elapsed = time.time() - start
        
        results = {
            'hours_back': hours_back,
            'num_instruments': len(instruments),
            'total_time': elapsed,
            'per_instrument': elapsed / len(instruments),
        }
        
        print(f"  Total time: {elapsed:.3f}s")
        print(f"  Per instrument: {results['per_instrument']:.3f}s")
        print(f"  Leverages caching: Yes")
        
        return results
    
    def benchmark_scaling(self, headline_counts: list = [100, 500, 1000, 2000]) -> dict:
        """Benchmark performance with different data sizes.
        
        Args:
            headline_counts: List of headline counts to test
            
        Returns:
            Dictionary with scaling results
        """
        print(f"\nBenchmark: Scaling Test")
        
        results = {}
        
        for count in headline_counts:
            print(f"\n  Testing with {count} headlines...")
            
            # Generate data
            headlines_file = self.generate_test_headlines(count, num_instruments=5)
            
            # Create engine
            config = NewsConfig(
                enabled=True,
                calendar_path="nonexistent.csv",
                headlines_path=str(headlines_file),
                headline_expiration_days=7
            )
            
            # Benchmark load time
            start = time.time()
            engine = NewsEngine(config)
            load_time = time.time() - start
            
            # Benchmark query time (100 queries)
            timestamp = pd.Timestamp.now()
            instruments = ["EURUSD", "GBPUSD", "XAUUSD"]
            
            start = time.time()
            for i in range(100):
                instrument = instruments[i % len(instruments)]
                score = engine.get_sentiment_score(instrument, timestamp)
            query_time = time.time() - start
            
            results[count] = {
                'load_time': load_time,
                'query_time_100': query_time,
                'per_query': (query_time / 100) * 1000,  # ms
                'indexed_instruments': len(engine.headlines_by_instrument)
            }
            
            print(f"    Load time: {load_time:.3f}s")
            print(f"    Query time (100): {query_time:.3f}s")
            print(f"    Per query: {results[count]['per_query']:.2f}ms")
            
            # Cleanup
            headlines_file.unlink()
        
        return results
    
    def run_full_benchmark(self):
        """Run complete benchmark suite."""
        print("=" * 70)
        print("NewsEngine Performance Benchmark (v1.2.3)")
        print("=" * 70)
        
        # Generate test data
        print("\nGenerating test data...")
        headlines_file = self.generate_test_headlines(1000, num_instruments=5)
        
        # Create engine
        config = NewsConfig(
            enabled=True,
            calendar_path="nonexistent.csv",
            headlines_path=str(headlines_file),
            headline_expiration_days=7
        )
        
        print("\nInitializing NewsEngine...")
        start = time.time()
        engine = NewsEngine(config)
        init_time = time.time() - start
        print(f"Initialization time: {init_time:.3f}s")
        print(f"Headlines loaded: {len(engine.headlines) if engine.headlines is not None else 0}")
        print(f"Indexed instruments: {len(engine.headlines_by_instrument)}")
        
        # Run benchmarks
        self.results['sentiment_score'] = self.benchmark_sentiment_score(engine, iterations=1000)
        self.results['instrument_lookup'] = self.benchmark_instrument_lookup(engine, iterations=10000)
        self.results['trend_analysis'] = self.benchmark_trend_analysis(engine, hours_back=24)
        
        # Cleanup
        headlines_file.unlink()
        
        # Scaling test
        self.results['scaling'] = self.benchmark_scaling([100, 500, 1000, 2000])
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 70)
        print("BENCHMARK SUMMARY")
        print("=" * 70)
        
        if 'sentiment_score' in self.results:
            r = self.results['sentiment_score']
            print(f"\nSentiment Score Performance:")
            print(f"  Cached queries: {r['hot_cache_per_call']:.2f}ms per call")
            print(f"  Uncached queries: {r['cold_cache_per_call']:.2f}ms per call")
            print(f"  Cache speedup: {r['speedup']:.1f}x")
        
        if 'instrument_lookup' in self.results:
            r = self.results['instrument_lookup']
            print(f"\nInstrument Lookup (Indexing):")
            print(f"  O(1) lookup time: {r['per_lookup']:.2f}μs")
        
        if 'scaling' in self.results:
            print(f"\nScaling Results:")
            for count, data in self.results['scaling'].items():
                print(f"  {count} headlines:")
                print(f"    Load: {data['load_time']:.3f}s, Query: {data['per_query']:.2f}ms/call")
        
        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)
        
        if 'sentiment_score' in self.results:
            speedup = self.results['sentiment_score']['speedup']
            if speedup > 50:
                print("✅ Cache is highly effective (>50x speedup)")
                print("   Current cache size (1000) is appropriate")
            elif speedup > 10:
                print("✅ Cache is effective (>10x speedup)")
                print("   Consider increasing cache size to 2000 for better hit rate")
            else:
                print("⚠️  Cache speedup is lower than expected")
                print("   Check cache hit rate and consider tuning")
        
        if 'scaling' in self.results:
            scaling_1000 = self.results['scaling'].get(1000, {})
            if scaling_1000.get('per_query', 999) < 10:
                print("✅ Excellent scaling performance (<10ms per query at 1000 headlines)")
            elif scaling_1000.get('per_query', 999) < 50:
                print("✅ Good scaling performance (<50ms per query at 1000 headlines)")
            else:
                print("⚠️  Performance degrades with scale, consider further optimization")


def main():
    """Main execution function."""
    benchmark = NewsEngineBenchmark()
    benchmark.run_full_benchmark()
    return 0


if __name__ == "__main__":
    sys.exit(main())
