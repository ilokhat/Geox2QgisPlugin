package fr.ign.cogit.squarer.process;

import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.util.Properties;

import fr.ign.cogit.cartagen.algorithms.polygon.SquarePolygonLS;
import fr.ign.cogit.geoxygene.api.feature.IFeature;
import fr.ign.cogit.geoxygene.api.feature.IFeatureCollection;
import fr.ign.cogit.geoxygene.api.feature.IPopulation;
import fr.ign.cogit.geoxygene.api.spatial.AbstractGeomFactory;
import fr.ign.cogit.geoxygene.api.spatial.coordgeom.IPolygon;
import fr.ign.cogit.geoxygene.api.spatial.geomroot.IGeometry;
import fr.ign.cogit.geoxygene.feature.DefaultFeature;
import fr.ign.cogit.geoxygene.feature.FT_FeatureCollection;
import fr.ign.cogit.geoxygene.spatial.geomengine.AbstractGeometryEngine;
import fr.ign.cogit.geoxygene.spatial.geomengine.GeometryEngine;
import fr.ign.cogit.geoxygene.util.conversion.ParseException;
import fr.ign.cogit.geoxygene.util.conversion.ShapefileReader;
import fr.ign.cogit.geoxygene.util.conversion.ShapefileWriter;

public class PolySquarer {

	public static void main(String[] args) throws ParseException {
		Properties creds = new Properties();
		Reader reader;
		GeometryEngine.init();
		AbstractGeomFactory factory = AbstractGeometryEngine.getFactory();
		if (args.length != 3) {
			System.out.println("Usage : squarer params.conf /path/to/input.shp /path/to/output.shp");
			System.exit(0);
		}
		try {
			reader = new FileReader(args[0]);
			creds.load(reader);
		} catch (IOException e) {
			e.printStackTrace();
		}
		String inputShape = args[1];
		String outPutShape = args[2];
		double rt = Double.parseDouble(creds.getProperty("rightTol"));
		double ft = Double.parseDouble(creds.getProperty("flatTol"));
		double srt = Double.parseDouble(creds.getProperty("semiRightTol"));

		IPopulation<IFeature> polygonShp = ShapefileReader.read(inputShape);
		SquarePolygonLS sqls = new SquarePolygonLS(rt, ft, srt);

		long begin = System.nanoTime();
		int i = 0;
		IFeatureCollection<IFeature> featC = new FT_FeatureCollection<>();
		for (IFeature f : polygonShp) {
			IGeometry geom = f.getGeom();
			IPolygon p = factory.createIPolygon(geom.coord());
			sqls.setPolygon(p);
			IPolygon pol2 = sqls.square();
			IFeature feat = new DefaultFeature(pol2);
			featC.add(feat);
			System.out.println(++i);
		}
		long end = System.nanoTime();
		System.out.println();
		System.out.println("computed in " + (end - begin) / 1000000 + " ms");
		System.out.println("-------------------------------------------");
		System.out.println("Writing out shape : " + outPutShape);
		ShapefileWriter.write(featC, outPutShape);
	}
}
