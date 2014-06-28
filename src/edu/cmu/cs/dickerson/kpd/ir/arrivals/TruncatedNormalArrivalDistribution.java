package edu.cmu.cs.dickerson.kpd.ir.arrivals;

import java.util.Random;

public class TruncatedNormalArrivalDistribution extends ArrivalDistribution {

	// Truncate the normal at +/- this many standard deviations from mean
	// (Warning: setting this to a small value will result in long draw times)
	private double stdevTrunc = Math.abs( 2.0 );
	
	public TruncatedNormalArrivalDistribution(int min, int max) {
		super(min, max);
	}

	/**
	 * Samples from the standard normal distribution, truncates to +/-2 stdevs,
	 * then scales this range to within [min, max], and rounds to nearest int
	 * @param min Minimum value returned by draw()
	 * @param max Maximum value returned by draw()
	 * @param random Random number generator to be used, if provided
	 */
	public TruncatedNormalArrivalDistribution(int min, int max, Random random) {
		super(min, max, random);
	}
	
	@Override
	public int draw() {
		
		if(min==max) { 
			return min; // point interval, return single point
		} else if(stdevTrunc <= 0) {
			return (max-min)/2; // point Gaussian distribution, return mean (halfway point between min and max)
		}
		
		// Repeatedly sample until we're within two unit stdevs of the mean
		double sample = 0.0;
		do {
			sample = random.nextGaussian();
		} while(sample > stdevTrunc || sample < -stdevTrunc);
		
		// Scales the sample to [0,1]
		double scaledSample = (sample+stdevTrunc)/(2*stdevTrunc);
		
		// Scale the sample to [min, max] and rounds to an integer
		return min + (int)Math.min(Math.round( scaledSample * (max-min) ), max);
	}

	@Override
	public String toString() {
		return "TruncatedNormal( [" + min + ", " + max + "], stdev=" + stdevTrunc + ")";
	}
}
